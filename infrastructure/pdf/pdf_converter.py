"""PDF 转换器 - 基础设施层

负责 PDF 文档解析和转换
"""

import os
import requests
from typing import Dict, Union, Optional, List
from pathlib import Path
import uuid
from loguru import logger

from src.core.document_converter import DocumentConverter


class PDFConverter:
    """PDF 转换器"""

    def __init__(self, converter_name: str = "markitdown", config: Optional[Dict] = None):
        """初始化 PDF 转换器

        Args:
            converter_name: 转换器名称 (markitdown/mineru)
            config: 配置字典
        """
        self.converter_name = converter_name
        self.config = config or {}

    def convert_file(self, file_path: Union[str, Path]) -> Dict:
        """转换本地 PDF 文件

        Args:
            file_path: PDF 文件路径

        Returns:
            包含文本内容和元数据的字典
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise ValueError(f"文件不存在：{file_path}")

        result = DocumentConverter.convert_to_text(
            str(file_path),
            converter_name=self.converter_name,
        )
        return result

    def convert_url(self, url: str) -> Dict:
        """从 URL 下载并转换 PDF

        Args:
            url: PDF 文件 URL

        Returns:
            包含文本内容和元数据的字典
        """
        result = DocumentConverter.convert_url_to_text(
            url,
            converter_name=self.converter_name,
        )
        return result

    def convert_batch(self, file_paths: List[Union[str, Path]]) -> List[Dict]:
        """批量转换 PDF 文件

        Args:
            file_paths: PDF 文件路径列表

        Returns:
            转换结果列表
        """
        results = []
        for file_path in file_paths:
            try:
                result = self.convert_file(file_path)
                results.append(result)
            except Exception as e:
                logger.error(f"转换文件 {file_path} 失败：{e}")
                results.append({"error": str(e), "file_path": str(file_path)})
        return results
