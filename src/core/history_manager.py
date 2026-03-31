import os
import json
import hashlib
import time
import csv
import yaml
from typing import Dict, Optional, Any, List
from pathlib import Path
from loguru import logger

class HistoryManager:
    """管理论文分析历史记录和缓存"""

    def __init__(self, storage_dir: str = "saved_analyses"):
        """初始化历史记录管理器

        Args:
            storage_dir (str): 存储目录路径，默认为项目根目录下的 saved_analyses
        """
        # 获取项目根目录
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.storage_dir = os.path.join(root_dir, storage_dir)
        self.index_file = os.path.join(self.storage_dir, "history.json")
        self.jsonl_file = os.path.join(self.storage_dir, "knowledge_base.jsonl")
        self.csv_file = os.path.join(self.storage_dir, "knowledge_base.csv")
        
        # 确保存储目录存在
        os.makedirs(self.storage_dir, exist_ok=True)
        self._init_csv()
        
        # 加载或初始化索引
        self.history_index = self._load_index()

    def _init_csv(self):
        """初始化知识库 CSV"""
        if not os.path.exists(self.csv_file):
            try:
                with open(self.csv_file, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["paper_id", "title", "year", "venue", "research_problem", "summary", "keywords", "innovation_points", "limitations", "method_tags", "dataset_tags", "model", "prompt_version", "total_tokens", "duration", "timestamp"])
            except Exception as e:
                logger.error(f"初始化知识库 CSV 失败: {e}")

    def _load_index(self) -> Dict:
        """加载历史记录索引"""
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载历史索引失败: {e}，将创建一个新的索引")
                return {}
        return {}

    def _save_index(self):
        """保存历史记录索引"""
        try:
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump(self.history_index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存历史索引失败: {e}")

    def compute_hash(self, input_source: str, is_file: bool = False) -> str:
        """计算输入源的哈希值

        Args:
            input_source (str): URL或文件路径
            is_file (bool): 是否为本地文件

        Returns:
            str: MD5哈希值
        """
        md5 = hashlib.md5()
        
        try:
            if is_file and os.path.exists(input_source):
                # 计算文件内容的哈希
                with open(input_source, "rb") as f:
                    # 分块读取以处理大文件
                    for chunk in iter(lambda: f.read(4096), b""):
                        md5.update(chunk)
            else:
                # 计算字符串(URL)的哈希
                md5.update(input_source.encode("utf-8"))
                
            return md5.hexdigest()
        except Exception as e:
            logger.error(f"计算哈希失败: {e}")
            # 如果失败，退回使用字符串哈希
            return hashlib.md5(str(input_source).encode("utf-8")).hexdigest()

    def get_cache_key(self, source_hash: str, prompt_name: str) -> str:
        """生成缓存键"""
        return f"{source_hash}_{prompt_name}"

    def get_analysis(self, source_hash: str, prompt_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """获取缓存的分析结果

        Args:
            source_hash (str): 输入源哈希，或直接传入完整 cache_key
            prompt_name (str, optional): 提示词模板名称；为空时尝试按 cache_key 直接读取

        Returns:
            Optional[Dict]: 如果存在缓存，返回包含 content 和 metadata 的字典，否则返回 None
        """
        cache_key = source_hash if prompt_name is None else self.get_cache_key(source_hash, prompt_name)
        
        if cache_key in self.history_index:
            entry = self.history_index[cache_key]
            file_path = os.path.join(self.storage_dir, entry["file_name"])
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # 尝试加载 JSON
                    structured_data = None
                    json_file_name = entry.get("json_file_name")
                    if json_file_name:
                        json_file_path = os.path.join(self.storage_dir, json_file_name)
                        if os.path.exists(json_file_path):
                            with open(json_file_path, "r", encoding="utf-8") as jf:
                                structured_data = json.load(jf)

                    logger.info(f"命中缓存: {entry['original_source']} (Prompt: {prompt_name})")
                    return {
                        "content": content,
                        "structured_data": structured_data,
                        "metadata": entry.get("metadata", {}),
                        "timestamp": entry.get("timestamp"),
                        "file_path": file_path
                    }
                except Exception as e:
                    logger.error(f"读取缓存文件失败: {e}")
            else:
                # 索引存在但文件不存在，清理索引
                del self.history_index[cache_key]
                self._save_index()
                
        return None

    def save_analysis(self, source: str, source_hash: str, prompt_name: str, content: str, metadata: Dict = None, structured_data: Dict = None, metrics: Dict = None) -> str:
        """保存分析结果

        Args:
            source (str): 原始输入源(URL或文件路径)
            source_hash (str): 输入源哈希
            prompt_name (str): 提示词模板名称
            content (str): 分析结果内容（如 Markdown 格式）
            metadata (Dict, optional): 元数据
            structured_data (Dict, optional): 结构化分析数据（写入 JSON 文件）
            metrics (Dict, optional): 审计指标 (model, usage, duration, prompt_version)

        Returns:
            str: 保存的主文件路径 (通常是 md 文件内容)
        """
        cache_key = self.get_cache_key(source_hash, prompt_name)
        metrics = metrics or {}
        
        # 生成文件名
        safe_name = "".join([c for c in os.path.basename(source) if c.isalpha() or c.isdigit() or c in ".-_"])
        if not safe_name:
            safe_name = "analysis"
        
        # 截断过长的文件名
        if len(safe_name) > 50:
            safe_name = safe_name[:50]
            
        base_file_name = f"{safe_name}_{prompt_name}_{source_hash[:8]}"
        file_name = f"{base_file_name}.md"
        file_path = os.path.join(self.storage_dir, file_name)
        
        # 保存内容
        try:
            # 1. 保存普通内容结果 (通常为 Markdown)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            json_file_name = None
            yaml_file_name = None
            # 2. 如果存在结构化数据，则一并保存对应的 JSON、YAML 和全局追加文件
            if structured_data is not None:
                # 将 metrics 注入结构化数据
                structured_data["audit_metrics"] = metrics
                
                json_file_name = f"{base_file_name}.json"
                json_file_path = os.path.join(self.storage_dir, json_file_name)
                with open(json_file_path, "w", encoding="utf-8") as jf:
                    json.dump(structured_data, jf, ensure_ascii=False, indent=2)
                
                try:
                    yaml_file_name = f"{base_file_name}.yaml"
                    yaml_file_path = os.path.join(self.storage_dir, yaml_file_name)
                    with open(yaml_file_path, "w", encoding="utf-8") as yf:
                        yaml.dump(structured_data, yf, allow_unicode=True, default_flow_style=False)
                except Exception as ye:
                    logger.error(f"YAML 写入失败: {ye}")

                try:
                    with open(self.jsonl_file, "a", encoding="utf-8") as jsonl_f:
                        jsonl_f.write(json.dumps(structured_data, ensure_ascii=False) + "\n")
                except Exception as jle:
                    logger.error(f"JSONL 追加写入失败: {jle}")

                try:
                    with open(self.csv_file, "a", encoding="utf-8", newline="") as csv_f:
                        writer = csv.writer(csv_f)
                        meta = structured_data.get("metadata", {})
                        analysis_block = structured_data.get("analysis", {})
                        total_tokens = metrics.get("usage", {}).get("total_tokens", 0)
                        writer.writerow([
                            structured_data.get("paper_id", ""),
                            meta.get("title", ""),
                            meta.get("year", ""),
                            meta.get("venue", ""),
                            analysis_block.get("research_problem", ""),
                            analysis_block.get("summary_one_sentence", ""),
                            ",".join(meta.get("keywords", [])),
                            ";".join(analysis_block.get("innovation_points", [])),
                            ";".join(analysis_block.get("limitations", [])),
                            ";".join(analysis_block.get("method_tags", [])),
                            ";".join(analysis_block.get("dataset_tags", [])),
                            metrics.get("model", ""),
                            metrics.get("prompt_version", ""),
                            total_tokens,
                            metrics.get("duration", 0),
                            time.time()
                        ])
                except Exception as ce:
                    logger.error(f"CSV 追加写入失败: {ce}")
                
            # 3. 更新索引
            self.history_index[cache_key] = {
                "file_name": file_name,
                "json_file_name": json_file_name,
                "yaml_file_name": yaml_file_name,
                "original_source": source,
                "prompt_name": prompt_name,
                "timestamp": time.time(),
                "metadata": metadata or {},
                "audit_metrics": metrics
            }
            self._save_index()
            logger.info(f"已保存分析结果并更新索引: {file_path}")
            if json_file_name:
                logger.info(f"已同时保存附加格式至: {json_file_name}, {yaml_file_name} 及知识库汇总文件")
            
            return file_path
        except Exception as e:
            logger.error(f"保存分析结果失败: {e}")
            raise e

    def get_history_entry(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """获取单条历史索引信息，不暴露内部存储细节给上层。"""
        entry = self.history_index.get(cache_key)
        return dict(entry) if entry else None

    def delete_history_item(self, cache_key: str, delete_file: bool = True) -> bool:
        """删除历史记录条目
        
        Args:
            cache_key (str): 缓存键
            delete_file (bool): 是否同时删除物理文件
            
        Returns:
            bool: 是否成功删除
        """
        if cache_key in self.history_index:
            entry = self.history_index[cache_key]
            
            if delete_file:
                # 删除 MD 文件
                file_path = os.path.join(self.storage_dir, entry.get("file_name", ""))
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        logger.info(f"已删除物理文件: {file_path}")
                    except Exception as e:
                        logger.error(f"删除物理文件失败: {e}")
                
                # 删除 JSON 文件（如果存在）
                json_file_name = entry.get("json_file_name")
                if json_file_name:
                    json_file_path = os.path.join(self.storage_dir, json_file_name)
                    if os.path.exists(json_file_path):
                        try:
                            os.remove(json_file_path)
                            logger.info(f"已删除结构化 JSON 物理文件: {json_file_path}")
                        except Exception as e:
                            logger.error(f"删除结构化 JSON 物理文件失败: {e}")
                
                # 删除 YAML 文件（如果存在）
                yaml_file_name = entry.get("yaml_file_name")
                if yaml_file_name:
                    yaml_file_path = os.path.join(self.storage_dir, yaml_file_name)
                    if os.path.exists(yaml_file_path):
                        try:
                            os.remove(yaml_file_path)
                            logger.info(f"已删除结构化 YAML 物理文件: {yaml_file_path}")
                        except Exception as e:
                            logger.error(f"删除结构化 YAML 物理文件失败: {e}")
            
            del self.history_index[cache_key]
            self._save_index()
            logger.info(f"已删除历史索引: {cache_key}")
            return True
        return False

    def list_history(self) -> list:
        """获取所有历史记录列表

        Returns:
            list: 包含历史记录信息的字典列表，按时间倒序排列
        """
        history_list = []
        for key, entry in self.history_index.items():
            # 确保包含必要字段
            item = {
                "cache_key": key,
                "original_source": entry.get("original_source", "Unknown"),
                "prompt_name": entry.get("prompt_name", "Unknown"),
                "timestamp": entry.get("timestamp", 0),
                "file_name": entry.get("file_name", ""),
                "file_path": os.path.join(self.storage_dir, entry.get("file_name", "")),
                "metadata": entry.get("metadata", {})
            }
            history_list.append(item)
        
        # 按时间戳倒序排列
        history_list.sort(key=lambda x: x["timestamp"], reverse=True)
        return history_list

    def get_multiple_analyses(self, cache_keys: List[str]) -> List[Dict]:
        """批量获取分析结果
        
        Args:
            cache_keys: 缓存键列表
            
        Returns:
            List[Dict]: 结构化数据列表
        """
        results = []
        for key in cache_keys:
            if key in self.history_index:
                entry = self.history_index[key]
                json_file_name = entry.get("json_file_name")
                if json_file_name:
                    json_file_path = os.path.join(self.storage_dir, json_file_name)
                    if os.path.exists(json_file_path):
                        try:
                            with open(json_file_path, "r", encoding="utf-8") as f:
                                data = json.load(f)
                                data["cache_key"] = key # 方便后续检索
                                results.append(data)
                        except Exception as e:
                            logger.error(f"批量读取 {json_file_path} 失败: {e}")
        return results
