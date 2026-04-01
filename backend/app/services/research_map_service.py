"""研究地图服务"""
import json
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger

from app.core.config import settings
from application.research_map_service import ResearchMapService as CoreResearchMapService
from src.core.config_loader import load_config


class ResearchMapService:
    """研究地图服务"""

    def __init__(self):
        """初始化服务"""
        self.config = load_config()
        self.core_service = CoreResearchMapService(self.config)

    def query(self, query: str, scope: str = "all", max_results: int = 5) -> Dict[str, Any]:
        """查询研究地图

        Args:
            query: 自然语言查询
            scope: 查询范围: all|active|compare
            max_results: 最大结果数

        Returns:
            查询结果
        """
        try:
            logger.info(f"研究地图查询: {query}, 范围={scope}")

            # 调用核心服务
            result = self.core_service.query_research_map(
                query=query,
                scope=scope,
                max_results=max_results,
            )

            return {
                "query": query,
                "answer": result.get("answer", ""),
                "sources": result.get("sources", []),
                "reasoning": result.get("reasoning", ""),
            }

        except Exception as e:
            logger.error(f"研究地图查询失败: {e}", exc_info=True)
            return {
                "query": query,
                "answer": f"查询失败: {str(e)}",
                "sources": [],
                "reasoning": "",
            }

    def get_map_data(self) -> Dict[str, Any]:
        """获取研究地图数据

        Returns:
            地图数据
        """
        try:
            # 调用核心服务获取地图数据
            data = self.core_service.get_map_data()

            return {
                "success": True,
                "data": data,
            }

        except Exception as e:
            logger.error(f"获取研究地图数据失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "data": None,
            }

    def rebuild_map(self) -> Dict[str, Any]:
        """重建研究地图

        Returns:
            重建结果
        """
        try:
            logger.info("开始重建研究地图")

            # 调用核心服务重建地图
            self.core_service.rebuild_map()

            return {
                "success": True,
                "message": "研究地图重建完成",
            }

        except Exception as e:
            logger.error(f"重建研究地图失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "重建研究地图失败",
            }
