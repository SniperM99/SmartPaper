"""论文分析服务"""
import json
import uuid
from pathlib import Path
from typing import Generator, Dict, Any, Optional
from loguru import logger

from app.core.config import settings
from application.paper_analysis_service import PaperAnalysisService
from application.multi_paper_service import MultiPaperService
from src.core.config_loader import load_config


class AnalysisService:
    """论文分析服务"""

    def __init__(self):
        """初始化服务"""
        self.config = load_config()
        self.paper_service = PaperAnalysisService(self.config)
        self.multi_paper_service = MultiPaperService(self.config)

    def analyze_from_file(
        self,
        file_path: str,
        role: str,
        task: str,
        domain: str,
        use_chain: bool = False,
    ) -> Generator[Dict[str, Any], None, None]:
        """从文件分析论文

        Args:
            file_path: 文件路径
            role: 分析角色
            task: 分析任务
            domain: 研究领域
            use_chain: 是否开启多轮分析链

        Yields:
            分析进度和结果
        """
        try:
            logger.info(f"开始分析文件: {file_path}")

            # 生成论文ID
            paper_id = uuid.uuid4().hex

            # 执行分析
            stream_gen = self.paper_service.analyze_stream(
                file_path, role=role, task=task, domain=domain
            )

            # 收集结果
            full_content = ""
            for chunk in stream_gen:
                full_content += chunk
                yield {
                    "type": "chunk",
                    "content": chunk,
                }

            # 保存结果
            output_file = self._save_result(paper_id, file_path, full_content)

            yield {
                "type": "final",
                "success": True,
                "paper_id": paper_id,
                "file_path": output_file,
            }

        except Exception as e:
            logger.error(f"文件分析失败: {e}", exc_info=True)
            yield {
                "type": "error",
                "error": str(e),
            }

    def analyze_from_url(
        self,
        url: str,
        role: str,
        task: str,
        domain: str,
        use_chain: bool = False,
    ) -> Generator[Dict[str, Any], None, None]:
        """从URL分析论文

        Args:
            url: 论文URL
            role: 分析角色
            task: 分析任务
            domain: 研究领域
            use_chain: 是否开启多轮分析链

        Yields:
            分析进度和结果
        """
        try:
            logger.info(f"开始分析URL: {url}")

            # 生成论文ID
            paper_id = uuid.uuid4().hex

            # 执行分析
            stream_gen = self.paper_service.analyze_url_stream(
                url, role=role, task=task, domain=domain
            )

            # 收集结果
            full_content = ""
            for chunk in stream_gen:
                full_content += chunk
                yield {
                    "type": "chunk",
                    "content": chunk,
                }

            # 保存结果
            output_file = self._save_result(paper_id, url, full_content)

            yield {
                "type": "final",
                "success": True,
                "paper_id": paper_id,
                "file_path": output_file,
            }

        except Exception as e:
            logger.error(f"URL分析失败: {e}", exc_info=True)
            yield {
                "type": "error",
                "error": str(e),
            }

    def compare_papers(
        self,
        main_paper_id: str,
        compare_paper_ids: list,
        role: str,
        domain: str,
        task: str,
    ) -> Generator[Dict[str, Any], None, None]:
        """多论文对比分析

        Args:
            main_paper_id: 主论文ID
            compare_paper_ids: 对比论文ID列表
            role: 分析角色
            domain: 研究领域
            task: 分析任务

        Yields:
            对比分析进度和结果
        """
        try:
            logger.info(
                f"开始多论文对比: 主论文={main_paper_id}, 对比论文={compare_paper_ids}"
            )

            # TODO: 从论文库获取论文路径
            # 这里需要与文献管理服务集成

            # 执行对比分析
            stream_gen = self.multi_paper_service.compare_papers_stream(
                main_paper_id=main_paper_id,
                compare_paper_ids=compare_paper_ids,
                role=role,
                domain=domain,
            )

            # 收集结果
            full_content = ""
            for chunk in stream_gen:
                full_content += chunk
                yield {
                    "type": "chunk",
                    "content": chunk,
                }

            # 保存结果
            output_file = self._save_result(
                f"compare_{main_paper_id}", "comparison", full_content
            )

            yield {
                "type": "final",
                "success": True,
                "file_path": output_file,
            }

        except Exception as e:
            logger.error(f"多论文对比失败: {e}", exc_info=True)
            yield {
                "type": "error",
                "error": str(e),
            }

    def _save_result(
        self, paper_id: str, source: str, content: str
    ) -> str:
        """保存分析结果

        Args:
            paper_id: 论文ID
            source: 来源（文件路径或URL）
            content: 分析内容

        Returns:
            保存的文件路径
        """
        # 生成安全的文件名
        safe_name = "".join(
            c for c in str(source).split("/")[-1] if c.isalnum() or c in ".-_"
        )
        output_file = settings.OUTPUT_DIR / f"analysis_{paper_id}_{safe_name}.md"

        # 写入文件
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"分析结果已保存: {output_file}")
        return str(output_file)
