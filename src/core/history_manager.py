import os
import json
import hashlib
import time
from typing import Dict, Optional, Any
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
        
        # 确保存储目录存在
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # 加载或初始化索引
        self.history_index = self._load_index()

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

    def get_analysis(self, source_hash: str, prompt_name: str) -> Optional[Dict[str, Any]]:
        """获取缓存的分析结果

        Args:
            source_hash (str): 输入源哈希
            prompt_name (str): 提示词模板名称

        Returns:
            Optional[Dict]: 如果存在缓存，返回包含 content 和 metadata 的字典，否则返回 None
        """
        cache_key = self.get_cache_key(source_hash, prompt_name)
        
        if cache_key in self.history_index:
            entry = self.history_index[cache_key]
            file_path = os.path.join(self.storage_dir, entry["file_name"])
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    logger.info(f"命中缓存: {entry['original_source']} (Prompt: {prompt_name})")
                    return {
                        "content": content,
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

    def save_analysis(self, source: str, source_hash: str, prompt_name: str, content: str, metadata: Dict = None) -> str:
        """保存分析结果

        Args:
            source (str): 原始输入源(URL或文件路径)
            source_hash (str): 输入源哈希
            prompt_name (str): 提示词模板名称
            content (str): 分析结果内容
            metadata (Dict, optional): 元数据

        Returns:
            str: 保存的文件路径
        """
        cache_key = self.get_cache_key(source_hash, prompt_name)
        
        # 生成文件名
        safe_name = "".join([c for c in os.path.basename(source) if c.isalpha() or c.isdigit() or c in ".-_"])
        if not safe_name:
            safe_name = "analysis"
        
        # 截断过长的文件名
        if len(safe_name) > 50:
            safe_name = safe_name[:50]
            
        file_name = f"{safe_name}_{prompt_name}_{source_hash[:8]}.md"
        file_path = os.path.join(self.storage_dir, file_name)
        
        # 保存内容
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            # 更新索引
            self.history_index[cache_key] = {
                "file_name": file_name,
                "original_source": source,
                "prompt_name": prompt_name,
                "timestamp": time.time(),
                "metadata": metadata or {}
            }
            self._save_index()
            logger.info(f"已保存分析结果并更新索引: {file_path}")
            
            return file_path
        except Exception as e:
            logger.error(f"保存分析结果失败: {e}")
            raise e
