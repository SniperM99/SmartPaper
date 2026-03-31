"""论文分析服务 - 应用编排层

负责单个论文分析的完整流程编排
"""

from typing import Dict, Optional, Generator, List, Any
from datetime import datetime
from domain.models import (
    PaperDocument,
    AnalysisResult,
    AnalysisTask,
    AnalysisStatus,
    PaperMetadata,
)
from infrastructure.llm.llm_client import LLMClient
from infrastructure.pdf.pdf_converter import PDFConverter
from application.literature_ingestion_service import LiteratureIngestionService
from src.core.prompt_manager import get_prompt
from src.core.history_manager import HistoryManager
from src.core.task_manager import TaskManager
from src.core.profile_manager import ProfileManager
from src.utils.section_splitter import SectionSplitter
from loguru import logger
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor


class PaperAnalysisService:
    """论文分析服务"""

    def __init__(self, config: Dict):
        """初始化分析服务

        Args:
            config: 应用配置字典
        """
        self.config = config
        self.llm_client = LLMClient(config)
        self.pdf_converter = PDFConverter(
            converter_name=config.get("document_converter", {}).get("converter_name", "markitdown"),
            config=config,
        )
        self.ingestion_service = LiteratureIngestionService(config)
        self.history_manager = HistoryManager()
        self.task_manager = TaskManager()
        self.profile_manager = ProfileManager()

    def _calculate_quality_metrics(self, sections: Dict[str, str], structured_data: Dict) -> Dict:
        """计算分析质量评分"""
        try:
            # 1. 文本提取质量 (基于长度和常见字符比例的简单启发式)
            text_extraction = 0.95 if sections else 0.0
            
            # 2. 章节识别完整度
            essential_sections = ["abstract", "method", "experiments", "results"]
            found_count = sum(1 for s in essential_sections if s in sections)
            section_detection = found_count / len(essential_sections)
            
            # 3. 证据支撑度 (基于 evidences 数量)
            evidences = structured_data.get("analysis", {}).get("evidences", [])
            evidence_support = min(1.0, len(evidences) / 5.0)  # 假设 5 条以上证据为满分
            
            # 4. 模型响应完整度
            analysis = structured_data.get("analysis", {})
            completeness_fields = ["summary_one_sentence", "research_problem", "background", "contributions"]
            valid_fields = sum(1 for f in completeness_fields if analysis.get(f) and analysis.get(f) != "文中未明确说明")
            analysis_completeness = valid_fields / len(completeness_fields)
            
            # 5. 总体可信度
            overall = (text_extraction + section_detection + evidence_support + analysis_completeness) / 4.0
            
            return {
                "text_extraction": round(text_extraction, 2),
                "section_detection": round(section_detection, 2),
                "analysis_completeness": round(analysis_completeness, 2),
                "evidence_support": round(evidence_support, 2),
                "overall_reliability": round(overall, 2)
            }
        except Exception as e:
            logger.error(f"质量评分计算失败: {e}")
            return {}

    def _analyze_by_sections(self, sections: Dict[str, str], prompt_name: str) -> str:
        """执行分段分析并汇总"""
        from langchain.schema import HumanMessage
        
        section_reports = []
        # 对核心章节进行独立解析
        target_sections = {
            "abstract": "摘要与背景",
            "method": "研究方法与技术路线",
            "experiments": "实验设计与结果",
            "conclusion": "结论与未来展望"
        }
        
        for sec_key, sec_display in target_sections.items():
            if sec_key in sections:
                logger.info(f"正在分析章节: {sec_key}...")
                sec_prompt_template = get_prompt("qc_section_analyzer")
                sec_prompt = sec_prompt_template.format(
                    section_name=sec_display,
                    text=sections[sec_key][:8000] # 限制单段长度
                )
                report = self.llm_client.chat([HumanMessage(content=sec_prompt)])
                section_reports.append(f"### 【{sec_display}】分析报告\n{report}")

        # 最终汇总
        logger.info("正在执行最终报告汇总(Synthesis)...")
        synth_prompt_template = get_prompt("qc_final_synthesizer")
        synth_prompt = synth_prompt_template.format(text="\n\n".join(section_reports))
        final_md = self.llm_client.chat([HumanMessage(content=synth_prompt)])
        
        return final_md

    def _extract_structured_data(self, content: str, paper_id: str, original_metadata: Dict, trace_info: Dict = None, quality_scores: Dict = None, parsed_document: Dict = None) -> tuple:
        """进行二次提取，获取结构化 JSON 数据"""
        from src.core.prompt_manager import get_prompt
        from langchain_core.messages import HumanMessage
        from domain.schemas import StructuredAnalysisData
        import json

        prompt_template = get_prompt("structured_extraction")
        prompt = prompt_template.format(text=content[:25000])

        try:
            logger.info("调用 LLM 进行结构化(JSON)重组...")
            llm_resp = self.llm_client.chat([HumanMessage(content=prompt)])
            response_content = llm_resp["content"]
            usage = llm_resp["usage"]
            
            # 去除可能存在的 markdown 标记
            clean_response = response_content.strip().replace("```json", "").replace("```", "").strip()
            structured_data = json.loads(clean_response)
            
            # 补全元数据
            if "metadata" not in structured_data or not structured_data["metadata"]:
                structured_data["metadata"] = original_metadata
            else:
                # 合并元数据
                for k, v in original_metadata.items():
                    if k not in structured_data["metadata"] or not structured_data["metadata"][k]:
                        structured_data["metadata"][k] = v
            
            structured_data["paper_id"] = paper_id

            if parsed_document:
                structured_data.setdefault("source", parsed_document.get("source", {}))
                structured_data.setdefault("document", parsed_document.get("document", {}))
                structured_data.setdefault("citations", parsed_document.get("citations", []))
                structured_data.setdefault("attachments", parsed_document.get("attachments", []))
                structured_data.setdefault("import_context", parsed_document.get("import_context", {}))

            # 注入过程信息
            if trace_info:
                structured_data["trace"] = trace_info
            
            if quality_scores:
                structured_data["quality_control"] = quality_scores
                
            # 转换为标准化对象并返回字典
            try:
                structured_obj = StructuredAnalysisData(**structured_data)
                return structured_obj.model_dump(), usage
            except Exception as ve:
                logger.warning(f"结构化数据 Pydantic 校验失败，改为输出完整降级对象: {ve}")
                fallback = self._build_fallback_structured_data(
                    paper_id=paper_id,
                    original_metadata=structured_data.get("metadata") or original_metadata,
                    parsed_document=parsed_document,
                    trace_info=trace_info,
                    quality_scores=quality_scores,
                    analysis_content=content,
                )
                return fallback, usage
                
        except Exception as e:
            logger.error(f"结构化数据提取失败: {e}")
            fallback = self._build_fallback_structured_data(
                paper_id=paper_id,
                original_metadata=original_metadata,
                parsed_document=parsed_document,
                trace_info=trace_info,
                quality_scores=quality_scores,
                analysis_content=content,
            )
            return fallback, {}

    @staticmethod
    def _build_fallback_structured_data(
        paper_id: str,
        original_metadata: Dict | None = None,
        parsed_document: Dict | None = None,
        trace_info: Dict | None = None,
        quality_scores: Dict | None = None,
        analysis_content: str = "",
    ) -> Dict:
        from domain.schemas import StructuredAnalysisData

        parsed_document = parsed_document or {}
        metadata = original_metadata or {}
        fallback = StructuredAnalysisData(
            paper_id=paper_id,
            source=parsed_document.get("source", {}),
            metadata=metadata,
            document=parsed_document.get("document", {}),
            citations=parsed_document.get("citations", []),
            attachments=parsed_document.get("attachments", []),
            import_context=parsed_document.get("import_context", {}),
            quality_control=quality_scores or {},
            trace=trace_info or {},
        )

        if analysis_content:
            fallback.analysis.summary_one_sentence = analysis_content.strip()[:300]

        return fallback.model_dump()

    def _run_analysis_chain(self, sections: Dict[str, str], role: str, domain: str) -> tuple:
        """运行多轮分析链：事实 -> 方法 -> 实验 -> 评价 -> 汇总"""
        from langchain_core.messages import HumanMessage
        from src.core.prompt_manager import compose_prompt, get_prompt
        
        chain_results = []
        total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        
        def update_usage(usage):
            for k in total_usage:
                total_usage[k] += usage.get(k, 0)

        # 1. 事实提取
        logger.info("分析链 第1轮: 事实层提取...")
        text_for_facts = (sections.get("abstract", "") + sections.get("introduction", ""))[:8000]
        p1 = compose_prompt(
            role=role, task="summarization", domain=domain, text=text_for_facts,
            user_context_str=self.profile_manager.get_context_string(),
            user_focus_list=self.profile_manager.get_analysis_focus()
        )
        r1_resp = self.llm_client.chat([HumanMessage(content=p1)])
        update_usage(r1_resp["usage"])
        chain_results.append(f"### 1. 事实与背景层报告\n{r1_resp['content']}")
        
        # 2. 方法论提取
        logger.info("分析链 第2轮: 方法层解析...")
        text_for_method = (sections.get("method", "") or text_for_facts)[:8000]
        p2 = compose_prompt(
            role=role, task="methodology", domain=domain, text=text_for_method,
            user_context_str=self.profile_manager.get_context_string(),
            user_focus_list=self.profile_manager.get_analysis_focus()
        )
        r2_resp = self.llm_client.chat([HumanMessage(content=p2)])
        update_usage(r2_resp["usage"])
        chain_results.append(f"### 2. 核心方法层报告\n{r2_resp['content']}")
        
        # 3. 实验证据提取
        logger.info("分析链 第3轮: 实验层评估...")
        text_for_exp = (sections.get("experiments", "") or sections.get("results", "") or text_for_facts)[:8000]
        p3 = compose_prompt(
            role=role, task="experiments", domain=domain, text=text_for_exp,
            user_context_str=self.profile_manager.get_context_string(),
            user_focus_list=self.profile_manager.get_analysis_focus()
        )
        r3_resp = self.llm_client.chat([HumanMessage(content=p3)])
        update_usage(r3_resp["usage"])
        chain_results.append(f"### 3. 实验验证层报告\n{r3_resp['content']}")
        
        # 4. 最终汇总 (Synthesis)
        logger.info("分析链 第4轮: 全局汇总与深度评价...")
        synth_prompt_template = get_prompt("qc_final_synthesizer")
        # 在汇总时注入 Role 和 Domain 的评价偏好
        role_pref_resp = self.llm_client.chat([HumanMessage(content=f"请简要描述以下角色的评价偏好和关注点：{role}")])
        update_usage(role_pref_resp["usage"])
        role_desc = role_pref_resp["content"]
        
        synth_intro = f"\n\n注意：本次分析以【{role}】视角进行，领域背景为【{domain}】。\n视角说明：{role_desc}\n"
        
        synth_prompt = synth_prompt_template.format(text=synth_intro + "\n\n".join(chain_results))
        final_resp = self.llm_client.chat([HumanMessage(content=synth_prompt)])
        update_usage(final_resp["usage"])
        
        return final_resp["content"], total_usage

    def analyze_file(
        self,
        file_path: str,
        role: str = "general_assistant",
        task: str = "summarization",
        domain: str = "general",
        prompt_name: Optional[str] = None, # 兼容参数名
        use_chain: bool = False,
        overwrite: bool = False
    ) -> Dict:
        """分析本地 PDF 文件"""
        import time
        from src.core.prompt_manager import _prompt_library, get_available_options, get_prompt, compose_prompt
        
        start_time_all = time.time()
        source_hash = self.history_manager.compute_hash(file_path, is_file=True)
        
        # 1. 检查缓存
        if not overwrite:
            cached_result = self.history_manager.get_analysis(source_hash, prompt_name or task)
            if cached_result:
                return cached_result

        logger.info(f"开始分析论文 (Role: {role}, Task: {task}, Domain: {domain}, Chain: {use_chain}): {file_path}")
        
        # 如果提供了 prompt_name，优先作为 task 使用
        if prompt_name:
            task = prompt_name
            
        task_key = f"{task}_{role}_{domain}"
        self.task_manager.update_task_status(file_path, task_key, AnalysisStatus.PARSING)

        try:
            # 1. 统一导入/解析
            parsed_document = self.ingestion_service.import_source(file_path)
            content = parsed_document.get("content", "")
            metadata = parsed_document.get("metadata", {})
            sections = parsed_document.get("section_map", {})

            # 3. 调用 LLM 分析
            self.task_manager.update_task_status(file_path, task_key, AnalysisStatus.ANALYZING)
            
            total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            def update_usage(usage):
                for k in total_usage:
                    total_usage[k] += usage.get(k, 0)

            if use_chain or task in ["phd_analysis", "full_analysis"]:
                analysis_content, chain_usage = self._run_analysis_chain(sections, role, domain)
                update_usage(chain_usage)
            else:
                options = get_available_options()
                if task in options.get("prompts", {}):
                    prompt_template = get_prompt(task)
                    prompt = prompt_template.format(text=content[:25000])
                else:
                    prompt = compose_prompt(role, task, domain, content[:25000], 
                                          self.profile_manager.get_context_string(),
                                          self.profile_manager.get_analysis_focus())
                
                from langchain_core.messages import HumanMessage
                llm_resp = self.llm_client.chat([HumanMessage(content=prompt)])
                analysis_content = llm_resp["content"]
                update_usage(llm_resp["usage"])

            # 4. 提取结构化数据与评分
            trace_info = {
                "role": role,
                "task": task,
                "domain": domain,
                "model_name": self.config.get("llm", {}).get(self.config["llm"]["provider"], {}).get("models", ["unknown"])[0]
            }
            
            # 第一遍提取用于评分
            temp_structured, extract_usage1 = self._extract_structured_data(analysis_content, source_hash, metadata, parsed_document=parsed_document)
            update_usage(extract_usage1)
            quality_scores = self._calculate_quality_metrics(sections, temp_structured or {})
            
            # 第二遍注入评分和过程信息
            structured_data, extract_usage2 = self._extract_structured_data(
                analysis_content, source_hash, metadata, trace_info=trace_info, quality_scores=quality_scores, parsed_document=parsed_document
            )
            update_usage(extract_usage2)
            
            duration = time.time() - start_time_all
            metrics = {
                "model": trace_info["model_name"],
                "usage": total_usage,
                "duration": round(duration, 2),
                "prompt_version": getattr(_prompt_library, "version", "unknown")
            }

            # 5. 保存结果
            saved_file = self.history_manager.save_analysis(
                source=file_path,
                source_hash=source_hash,
                prompt_name=task,
                content=analysis_content,
                metadata=metadata,
                structured_data=structured_data,
                metrics=metrics
            )

            self.task_manager.update_task_status(
                file_path, task_key, AnalysisStatus.COMPLETED, 
                output_path=saved_file,
                metrics={
                    "token_usage": total_usage.get("total_tokens", 0),
                    "duration": round(duration, 2)
                }
            )
            
            return {
                "content": analysis_content,
                "structured_data": structured_data,
                "metadata": metadata,
                "parsed_document": parsed_document,
                "audit_metrics": metrics,
                "file_path": saved_file
            }

        except Exception as e:
            logger.error(f"分析文件失败: {e}")
            self.task_manager.update_task_status(file_path, task_key, AnalysisStatus.FAILED, error_message=str(e))
            raise e

    def analyze_url(
        self,
        url: str,
        role: str = "general_assistant",
        task: str = "summarization",
        domain: str = "general",
        prompt_name: Optional[str] = None,
        use_chain: bool = False,
        description: Optional[str] = None,
        overwrite: bool = False
    ) -> Dict:
        """分析在线论文 URL"""
        import time
        from src.core.prompt_manager import _prompt_library, get_available_options, get_prompt, compose_prompt
        
        start_time_all = time.time()
        source_hash = self.history_manager.compute_hash(url, is_file=False)
        
        # 1. 检查缓存
        if not overwrite:
            cached_result = self.history_manager.get_analysis(source_hash, prompt_name or task)
            if cached_result:
                return cached_result

        logger.info(f"开始分析 URL (Role: {role}, Task: {task}, Domain: {domain}, Chain: {use_chain}): {url}")
        
        if prompt_name:
            task = prompt_name
            
        task_key = f"{task}_{role}_{domain}"
        self.task_manager.update_task_status(url, task_key, AnalysisStatus.PARSING)

        try:
            # 1. 统一导入/解析
            parsed_document = self.ingestion_service.import_source(url, metadata={"description": description} if description else None)
            content = parsed_document.get("content", "")
            metadata = parsed_document.get("metadata", {})
            if description: metadata["description"] = description
            metadata["url"] = url
            sections = parsed_document.get("section_map", {})

            # 3. 调用 LLM 分析
            self.task_manager.update_task_status(url, task_key, AnalysisStatus.ANALYZING)
            
            total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            def update_usage(usage):
                for k in total_usage:
                    total_usage[k] += usage.get(k, 0)

            if use_chain or task in ["phd_analysis", "full_analysis"]:
                analysis_content, chain_usage = self._run_analysis_chain(sections, role, domain)
                update_usage(chain_usage)
            else:
                options = get_available_options()
                if task in options.get("prompts", {}):
                    prompt_template = get_prompt(task)
                    prompt = prompt_template.format(text=content[:25000])
                else:
                    prompt = compose_prompt(role, task, domain, content[:25000], 
                                          self.profile_manager.get_context_string(),
                                          self.profile_manager.get_analysis_focus())
                
                from langchain_core.messages import HumanMessage
                llm_resp = self.llm_client.chat([HumanMessage(content=prompt)])
                analysis_content = llm_resp["content"]
                update_usage(llm_resp["usage"])

            # 4. 提取结构化数据与评分
            trace_info = {
                "role": role, "task": task, "domain": domain,
                "model_name": self.config.get("llm", {}).get(self.config["llm"]["provider"], {}).get("models", ["unknown"])[0]
            }
            
            # 第一遍提取用于评分
            temp_structured, extract_usage1 = self._extract_structured_data(analysis_content, source_hash, metadata, parsed_document=parsed_document)
            update_usage(extract_usage1)
            quality_scores = self._calculate_quality_metrics(sections, temp_structured or {})
            
            # 第二遍注入评分和过程信息
            structured_data, extract_usage2 = self._extract_structured_data(
                analysis_content, source_hash, metadata, trace_info=trace_info, quality_scores=quality_scores, parsed_document=parsed_document
            )
            update_usage(extract_usage2)
            
            duration = time.time() - start_time_all
            metrics = {
                "model": trace_info["model_name"],
                "usage": total_usage,
                "duration": round(duration, 2),
                "prompt_version": getattr(_prompt_library, "version", "unknown")
            }

            # 5. 保存结果
            saved_file = self.history_manager.save_analysis(
                source=url,
                source_hash=source_hash,
                prompt_name=task,
                content=analysis_content,
                metadata=metadata,
                structured_data=structured_data,
                metrics=metrics
            )

            self.task_manager.update_task_status(
                url, task_key, AnalysisStatus.COMPLETED, 
                output_path=saved_file,
                metrics={
                    "token_usage": total_usage.get("total_tokens", 0),
                    "duration": round(duration, 2)
                }
            )
            
            return {
                "content": analysis_content,
                "structured_data": structured_data,
                "metadata": metadata,
                "parsed_document": parsed_document,
                "audit_metrics": metrics,
                "file_path": saved_file
            }

        except Exception as e:
            logger.error(f"分析 URL 失败: {e}")
            self.task_manager.update_task_status(url, task_key, AnalysisStatus.FAILED, error_message=str(e))
            raise e

    def analyze_stream(
        self,
        file_path: str,
        role: str = "general_assistant",
        task: str = "summarization",
        domain: str = "general",
        prompt_name: Optional[str] = None,
    ) -> Generator[str, None, None]:
        """流式分析论文"""
        logger.info(f"开始流式分析：{file_path}")
        if prompt_name: task = prompt_name

        try:
            yield "🚀 正在转换 PDF...\n\n"
            convert_result = self.pdf_converter.convert_file(file_path)
            content = convert_result.get("text_content", "")
            yield "✅ PDF 转换完成\n\n"

            from src.core.prompt_manager import compose_prompt, get_prompt, get_available_options
            options = get_available_options()
            if task in options.get("prompts", {}):
                prompt_template = get_prompt(task)
                prompt = prompt_template.format(text=content)
            else:
                prompt = compose_prompt(
                    role=role, task=task, domain=domain, text=content,
                    user_context_str=self.profile_manager.get_context_string(),
                    user_focus_list=self.profile_manager.get_analysis_focus()
                )

            yield f"📝 分析中 (角色: {role}, 任务: {task}, 领域: {domain})...\n\n"
            from langchain_core.messages import HumanMessage
            for chunk in self.llm_client.chat_stream([HumanMessage(content=prompt)]):
                yield chunk

            yield "\n\n✅ 分析完成"
        except Exception as e:
            yield f"\n\n❌ 错误：{str(e)}"
            raise

        except Exception as e:
            yield f"\n\n❌ 错误：{str(e)}"
            raise

    def analyze_url_stream(
        self,
        url: str,
        role: str = "general_assistant",
        task: str = "summarization",
        domain: str = "general",
        prompt_name: Optional[str] = None,
    ) -> Generator[str, None, None]:
        """流式分析在线论文 URL"""
        logger.info(f"开始流式分析 URL：{url}")
        if prompt_name: task = prompt_name

        try:
            yield "🚀 正在下载并转换 PDF...\n\n"
            convert_result = self.pdf_converter.convert_url(url)
            content = convert_result.get("text_content", "")
            yield "✅ PDF 转换完成\n\n"

            from src.core.prompt_manager import compose_prompt, get_prompt, get_available_options
            options = get_available_options()
            if task in options.get("prompts", {}):
                prompt_template = get_prompt(task)
                prompt = prompt_template.format(text=content)
            else:
                prompt = compose_prompt(
                    role=role, task=task, domain=domain, text=content,
                    user_context_str=self.profile_manager.get_context_string(),
                    user_focus_list=self.profile_manager.get_analysis_focus()
                )

            yield f"📝 分析中 (角色: {role}, 任务: {task}, 领域: {domain})...\n\n"
            from langchain_core.messages import HumanMessage
            for chunk in self.llm_client.chat_stream([HumanMessage(content=prompt)]):
                yield chunk

            yield "\n\n✅ 分析完成"
        except Exception as e:
            yield f"\n\n❌ 错误：{str(e)}"
            raise

    def ask_question(self, paper_id: str, question: str) -> str:
        """针对特定论文进行追问
        
        Args:
            paper_id: 论文 ID (通常是文件哈希或 URL)
            question: 用户的问题
            
        Returns:
            AI 的回答
        """
        # 1. 获取论文内容
        history = self.history_manager.get_analysis(paper_id)
        if not history:
            return "❌ 找不到该论文的分析记录，请先进行解析。"
        
        # 2. 构造 RAG 提示词 (简单实现)
        paper_text = history.get("text_content", "") or history.get("content", "")
        
        prompt = f"""你是一个专业的科研助手。请基于以下论文内容回答用户的问题。
        如果论文中没有提到相关信息，请诚实说明，不要编造。

        ## 论文内容：
        {paper_text[:25000]}

        ## 用户问题：
        {question}

        ## 回答要求：
        - 语言准确、客观。
        - 引用论文中的具体章节或证据。
        - 保持学术讨论的深度。
        """
        
        from langchain_core.messages import HumanMessage
        llm_resp = self.llm_client.chat([HumanMessage(content=prompt)])
        return llm_resp["content"]

    def calculate_relevance(self, paper_id: str) -> Dict[str, Any]:
        """计算论文与用户研究画像的相关度
        
        Args:
            paper_id: 论文 ID
            
        Returns:
            包含相关度评分 and 分析的字典
        """
        history = self.history_manager.get_analysis(paper_id)
        if not history:
            return {"error": "找不到论文记录"}
            
        user_context = self.profile_manager.get_context_string()
        paper_text = history.get("text_content", "") or history.get("content", "")
        
        prompt = f"""你是一个科研导师。请评估以下论文与用户当前研究课题的相关性。

        ## 用户个人画像与课题：
        {user_context}

        ## 待评估论文内容：
        {paper_text[:20000]}

        ## 评估要求：
        请输出一个 JSON 对象，包含以下字段：
        - relevance_score: 0-100 的整数评分
        - matching_points: 匹配点列表（为什么相关）
        - gap_points: 差异点列表（哪里不相关，或该论文未涵盖的你的课题点）
        - usage_suggestion: 具体应用建议（你可以如何利用这篇论文）

        只输出 JSON，不要任何 Markdown 或寒暄。
        """
        
        from langchain_core.messages import HumanMessage
        llm_resp = self.llm_client.chat([HumanMessage(content=prompt)])
        response_content = llm_resp["content"]
        
        try:
            # 去除可能存在的 markdown 标记
            clean_response = response_content.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(clean_response)
        except Exception:
            return {"error": "无法解析相关性评分报告", "raw_content": response_content}

    def process_batch(
        self,
        sources: List[str],
        role: str = "general_assistant",
        task: str = "summarization",
        domain: str = "general",
        prompt_name: Optional[str] = None,
        use_chain: bool = False,
        resume: bool = True,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """批量处理论文"""
        if prompt_name: task = prompt_name
        task_key = f"{task}_{role}_{domain}"
        
        logger.info(f"开始批量处理任务 (Role: {role}, Task: {task}, Domain: {domain}, Chain: {use_chain}), 共 {len(sources)} 个目标")
        
        for source in sources:
            # 初始化或检查状态
            self.task_manager.get_or_create_task(source, task_key)
            
            if resume and not overwrite:
                if self.task_manager.is_completed(source, task_key):
                    logger.info(f"跳过已完成任务: {source}")
                    continue
            
            try:
                if source.startswith(("http://", "https://")):
                    self.analyze_url(source, role=role, task=task, domain=domain, use_chain=use_chain)
                else:
                    self.analyze_file(source, role=role, task=task, domain=domain, use_chain=use_chain)
            except Exception as e:
                logger.error(f"批量任务中某项处理失败 ({source}): {e}")

        return self.task_manager.get_batch_stats()
