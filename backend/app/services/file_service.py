"""文件服务"""
import os
import uuid
from pathlib import Path
from typing import Dict, Any, Generator
from loguru import logger

from app.core.config import settings


class FileService:
    """文件服务"""

    def __init__(self):
        """初始化服务"""
        self.upload_dir = settings.UPLOAD_DIR
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def save_upload_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """保存上传的文件

        Args:
            file_content: 文件内容
            filename: 文件名

        Returns:
            保存结果
        """
        try:
            # 生成文件ID
            file_id = uuid.uuid4().hex

            # 生成安全的文件名
            safe_filename = f"{file_id}_{filename}"
            file_path = self.upload_dir / safe_filename

            # 写入文件
            with open(file_path, "wb") as f:
                f.write(file_content)

            logger.info(f"文件已保存: {file_path}")

            return {
                "file_id": file_id,
                "filename": filename,
                "size": len(file_content),
                "path": str(file_path),
                "status": "uploaded",
            }

        except Exception as e:
            logger.error(f"保存文件失败: {e}", exc_info=True)
            return {
                "file_id": "",
                "filename": filename,
                "size": 0,
                "path": "",
                "status": "failed",
                "error": str(e),
            }

    def get_file(self, file_path: str) -> Generator[bytes, None, None]:
        """读取文件流

        Args:
            file_path: 文件路径

        Yields:
            文件内容块
        """
        try:
            path = Path(file_path)

            if not path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")

            if not path.is_file():
                raise ValueError(f"路径不是文件: {file_path}")

            with open(path, "rb") as f:
                while chunk := f.read(8192):
                    yield chunk

        except Exception as e:
            logger.error(f"读取文件失败: {e}", exc_info=True)
            raise

    def delete_file(self, file_path: str) -> bool:
        """删除文件

        Args:
            file_path: 文件路径

        Returns:
            是否成功
        """
        try:
            path = Path(file_path)

            if path.exists():
                path.unlink()
                logger.info(f"文件已删除: {file_path}")
                return True

            return False

        except Exception as e:
            logger.error(f"删除文件失败: {e}", exc_info=True)
            return False

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """获取文件信息

        Args:
            file_path: 文件路径

        Returns:
            文件信息
        """
        try:
            path = Path(file_path)

            if not path.exists():
                return {
                    "exists": False,
                }

            stat = path.stat()

            return {
                "exists": True,
                "filename": path.name,
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "extension": path.suffix,
            }

        except Exception as e:
            logger.error(f"获取文件信息失败: {e}", exc_info=True)
            return {
                "exists": False,
                "error": str(e),
            }
