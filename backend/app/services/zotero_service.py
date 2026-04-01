"""Zotero 集成服务"""
from typing import List, Dict, Any, Optional
from loguru import logger

from app.core.config import settings
from application.zotero_integration_service import ZoteroIntegrationService
from src.core.config_loader import load_config


class ZoteroService:
    """Zotero 集成服务"""

    def __init__(self):
        """初始化服务"""
        self.config = load_config()
        self.core_service = ZoteroIntegrationService(self.config)

    def get_collections(self) -> List[Dict[str, Any]]:
        """获取 Zotero 收藏夹列表

        Returns:
            收藏夹列表
        """
        try:
            logger.info("获取 Zotero 收藏夹列表")

            collections = self.core_service.get_collections()

            return collections

        except Exception as e:
            logger.error(f"获取收藏夹失败: {e}", exc_info=True)
            return []

    def get_items(
        self, collection_id: Optional[str] = None, limit: int = 50
    ) -> Dict[str, Any]:
        """获取 Zotero 文献条目

        Args:
            collection_id: 收藏夹ID，不指定则获取全部
            limit: 限制数量

        Returns:
            文献条目列表
        """
        try:
            logger.info(f"获取 Zotero 文献条目: collection_id={collection_id}")

            items = self.core_service.get_items(
                collection_id=collection_id, limit=limit
            )

            return {
                "items": items,
                "total": len(items),
            }

        except Exception as e:
            logger.error(f"获取文献条目失败: {e}", exc_info=True)
            return {
                "items": [],
                "total": 0,
                "error": str(e),
            }

    def import_items(
        self, item_keys: List[str], analysis_config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """从 Zotero 导入文献到 SmartPaper

        Args:
            item_keys: 文献条目key列表
            analysis_config: 分析配置（可选）

        Returns:
            导入结果
        """
        try:
            logger.info(f"从 Zotero 导入文献: {item_keys}")

            results = []
            success_count = 0
            failed_count = 0

            for item_key in item_keys:
                try:
                    # 获取附件
                    attachments = self.core_service.get_item_attachments(item_key)

                    if not attachments:
                        logger.warning(f"条目 {item_key} 没有附件")
                        failed_count += 1
                        results.append(
                            {
                                "item_key": item_key,
                                "success": False,
                                "error": "没有附件",
                            }
                        )
                        continue

                    # 下载并导入第一个附件
                    attachment = attachments[0]
                    file_path = self.core_service.download_attachment(attachment)

                    # TODO: 导入到论文库
                    # 这里需要调用 ingestion_service

                    success_count += 1
                    results.append(
                        {
                            "item_key": item_key,
                            "success": True,
                            "file_path": file_path,
                        }
                    )

                except Exception as e:
                    logger.error(f"导入条目 {item_key} 失败: {e}")
                    failed_count += 1
                    results.append(
                        {
                            "item_key": item_key,
                            "success": False,
                            "error": str(e),
                        }
                    )

            return {
                "status": "completed",
                "total": len(item_keys),
                "processed": success_count,
                "failed": failed_count,
                "results": results,
            }

        except Exception as e:
            logger.error(f"Zotero 批量导入失败: {e}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e),
                "total": 0,
                "processed": 0,
                "failed": 0,
                "results": [],
            }

    def test_connection(self) -> Dict[str, Any]:
        """测试 Zotero 连接

        Returns:
            连接测试结果
        """
        try:
            logger.info("测试 Zotero 连接")

            # 尝试获取一个条目
            items = self.core_service.get_items(limit=1)

            return {
                "success": True,
                "message": "Zotero 连接正常",
                "user_id": self.config.get("zotero", {}).get("user_id", ""),
            }

        except Exception as e:
            logger.error(f"Zotero 连接失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Zotero 连接失败: {str(e)}",
            }
