"""文献导入服务"""
import uuid
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger

from app.core.config import settings
from application.literature_ingestion_service import LiteratureIngestionService
from src.core.config_loader import load_config


class IngestionService:
    """文献导入服务"""

    def __init__(self):
        """初始化服务"""
        self.config = load_config()
        self.ingestion_service = LiteratureIngestionService(self.config)
        # TODO: 初始化文献库存储

    def ingest_local_paths(
        self, paths: List[str], recursive: bool = False
    ) -> Dict[str, Any]:
        """从本地路径批量导入文献

        Args:
            paths: 文件或文件夹路径列表
            recursive: 是否递归扫描子文件夹

        Returns:
            导入结果
        """
        try:
            logger.info(f"开始批量导入: {paths}, 递归={recursive}")

            task_id = uuid.uuid4().hex
            results = []
            success_count = 0
            failed_count = 0

            for path in paths:
                path_obj = Path(path)

                if path_obj.is_file():
                    # 处理单个文件
                    result = self._ingest_single_file(path_obj)
                    if result["success"]:
                        success_count += 1
                    else:
                        failed_count += 1
                    results.append(result)

                elif path_obj.is_dir():
                    # 处理文件夹
                    if recursive:
                        files = list(path_obj.rglob("*.pdf"))
                    else:
                        files = list(path_obj.glob("*.pdf"))

                    for file in files:
                        result = self._ingest_single_file(file)
                        if result["success"]:
                            success_count += 1
                        else:
                            failed_count += 1
                        results.append(result)

            return {
                "task_id": task_id,
                "status": "completed",
                "total": len(results),
                "processed": success_count,
                "failed": failed_count,
                "results": results,
            }

        except Exception as e:
            logger.error(f"批量导入失败: {e}", exc_info=True)
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e),
                "total": 0,
                "processed": 0,
                "failed": 0,
                "results": [],
            }

    def ingest_from_arxiv(self, arxiv_ids: List[str]) -> Dict[str, Any]:
        """从 arXiv 下载并导入文献

        Args:
            arxiv_ids: arXiv ID列表

        Returns:
            导入结果
        """
        try:
            logger.info(f"开始从 arXiv 下载: {arxiv_ids}")

            task_id = uuid.uuid4().hex
            results = []
            success_count = 0
            failed_count = 0

            for arxiv_id in arxiv_ids:
                try:
                    # 构造arXiv URL
                    url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

                    # 下载并导入
                    result = self.ingestion_service.ingest_from_url(url)

                    results.append(
                        {
                            "arxiv_id": arxiv_id,
                            "success": True,
                            "title": result.get("title", ""),
                            "paper_id": result.get("paper_id", ""),
                        }
                    )
                    success_count += 1

                except Exception as e:
                    logger.error(f"下载 {arxiv_id} 失败: {e}")
                    results.append(
                        {
                            "arxiv_id": arxiv_id,
                            "success": False,
                            "error": str(e),
                        }
                    )
                    failed_count += 1

            return {
                "task_id": task_id,
                "status": "completed",
                "total": len(arxiv_ids),
                "processed": success_count,
                "failed": failed_count,
                "results": results,
            }

        except Exception as e:
            logger.error(f"arXiv 批量下载失败: {e}", exc_info=True)
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e),
                "total": 0,
                "processed": 0,
                "failed": 0,
                "results": [],
            }

    def _ingest_single_file(self, file_path: Path) -> Dict[str, Any]:
        """导入单个文件

        Args:
            file_path: 文件路径

        Returns:
            导入结果
        """
        try:
            logger.info(f"正在导入文件: {file_path}")

            # 调用导入服务
            result = self.ingestion_service.ingest_file(str(file_path))

            # TODO: 保存到论文库
            paper_id = uuid.uuid4().hex

            return {
                "success": True,
                "file_path": str(file_path),
                "title": result.get("title", file_path.stem),
                "paper_id": paper_id,
            }

        except Exception as e:
            logger.error(f"导入文件失败 {file_path}: {e}")
            return {
                "success": False,
                "file_path": str(file_path),
                "error": str(e),
            }

    def get_paper_list(self) -> List[Dict[str, Any]]:
        """获取论文库列表

        Returns:
            论文列表
        """
        # TODO: 从数据库或文件系统读取论文列表
        return []

    def get_paper_detail(self, paper_id: str) -> Dict[str, Any]:
        """获取论文详情

        Args:
            paper_id: 论文ID

        Returns:
            论文详情
        """
        # TODO: 实现论文详情获取
        return {}

    def delete_paper(self, paper_id: str) -> Dict[str, Any]:
        """删除论文

        Args:
            paper_id: 论文ID

        Returns:
            删除结果
        """
        # TODO: 实现论文删除
        return {"success": True, "message": "论文已删除"}
