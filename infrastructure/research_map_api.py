"""研究地图 API 服务。"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
import uvicorn
import threading

from application.research_map_service import ResearchMapService
from src.core.history_manager import HistoryManager
from interfaces.research_map_api import (
    ResearchMapRequest,
    ResearchMapResponse,
    EntityDetailRequest,
    EntityDetailResponse,
    SearchRequest,
    SearchResponse,
    ExportRequest,
)

router = APIRouter(prefix="/api", tags=["研究地图"])

# 全局服务实例
research_map_service = ResearchMapService()
history_manager = HistoryManager()


@router.get("/research-map", response_model=Dict[str, Any])
async def get_research_map(
    cacheKeys: Optional[str] = Query(None, description="知识卡缓存键列表，逗号分隔")
) -> Dict[str, Any]:
    """
    获取研究地图数据。

    Args:
        cacheKeys: 知识卡缓存键列表，逗号分隔

    Returns:
        研究地图数据
    """
    try:
        if cacheKeys:
            keys = [k.strip() for k in cacheKeys.split(",") if k.strip()]
            data = research_map_service.build_from_cache_keys(keys)
        else:
            # 使用默认的论文列表
            # TODO: 从 session state 获取选中的论文
            cards = []
            data = research_map_service.build_from_cards(cards)

        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取研究地图数据失败: {str(e)}")


@router.post("/research-map", response_model=Dict[str, Any])
async def create_research_map(request: ResearchMapRequest) -> Dict[str, Any]:
    """
    创建研究地图。

    Args:
        request: 研究地图请求

    Returns:
        研究地图数据
    """
    try:
        if request.cache_keys:
            data = research_map_service.build_from_cache_keys(request.cache_keys)
        else:
            data = research_map_service.build_from_cards([])

        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建研究地图失败: {str(e)}")


@router.get("/entities/{entity_id}", response_model=Dict[str, Any])
async def get_entity_detail(entity_id: str) -> Dict[str, Any]:
    """
    获取实体详情。

    Args:
        entity_id: 实体 ID

    Returns:
        实体详情
    """
    try:
        # 从缓存的研究地图中查找实体
        # TODO: 实现实体详情查询逻辑
        entity = {
            "id": entity_id,
            "label": "Entity",
            "entity_type": "topic",
        }

        return {
            "status": "success",
            "entity": entity,
            "related_papers": [],
            "relations": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取实体详情失败: {str(e)}")


@router.get("/search", response_model=Dict[str, Any])
async def search_nodes(
    q: str = Query(..., description="搜索关键词"),
    entityTypes: Optional[str] = Query(None, description="实体类型过滤，逗号分隔"),
    minMentions: Optional[int] = Query(None, description="最小提及数")
) -> Dict[str, Any]:
    """
    搜索节点。

    Args:
        q: 搜索关键词
        entityTypes: 实体类型过滤，逗号分隔
        minMentions: 最小提及数

    Returns:
        搜索结果
    """
    try:
        # TODO: 实现搜索逻辑
        results = []

        filters = {}
        if entityTypes:
            filters["entity_types"] = [t.strip() for t in entityTypes.split(",") if t.strip()]
        if minMentions is not None:
            filters["min_mentions"] = minMentions

        return {
            "status": "success",
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/research-map/export")
async def export_research_map(
    format: str = Query("json", description="导出格式：json/svg"),
    cacheKeys: Optional[str] = Query(None, description="知识卡缓存键列表，逗号分隔")
):
    """
    导出研究地图。

    Args:
        format: 导出格式（json/svg）
        cacheKeys: 知识卡缓存键列表，逗号分隔

    Returns:
        导出的文件
    """
    try:
        if cacheKeys:
            keys = [k.strip() for k in cacheKeys.split(",") if k.strip()]
            data = research_map_service.build_from_cache_keys(keys)
        else:
            data = research_map_service.build_from_cards([])

        if format == "json":
            from fastapi.responses import JSONResponse
            return JSONResponse(content=data)
        elif format == "svg":
            # TODO: 实现 SVG 导出
            return {"error": "SVG export not implemented yet"}
        else:
            raise HTTPException(status_code=400, detail=f"不支持的导出格式: {format}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


class ResearchMapAPIServer:
    """研究地图 API 服务器。"""

    def __init__(self, host: str = "127.0.0.1", port: int = 8001):
        self.host = host
        self.port = port
        self.app = None
        self.server_thread = None

    def create_app(self):
        """创建 FastAPI 应用。"""
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware

        app = FastAPI(
            title="SmartPaper 研究地图 API",
            description="提供研究地图数据接口",
            version="1.0.0"
        )

        # 配置 CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # 注册路由
        app.include_router(router)

        @app.get("/")
        async def root():
            return {
                "message": "SmartPaper 研究地图 API",
                "version": "1.0.0",
                "endpoints": {
                    "研究地图": "/api/research-map",
                    "实体详情": "/api/entities/{entity_id}",
                    "搜索": "/api/search",
                    "导出": "/api/research-map/export"
                }
            }

        @app.get("/health")
        async def health():
            return {"status": "healthy"}

        return app

    def start(self):
        """在后台线程启动服务器。"""
        if self.server_thread and self.server_thread.is_alive():
            return

        self.app = self.create_app()

        def run_server():
            uvicorn.run(
                self.app,
                host=self.host,
                port=self.port,
                log_level="info"
            )

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()

    def stop(self):
        """停止服务器。"""
        # FastAPI/uvicorn 的停止需要更复杂的处理
        # 这里只是简单标记
        pass


# 全局 API 服务器实例
_api_server: Optional[ResearchMapAPIServer] = None


def start_api_server(host: str = "127.0.0.1", port: int = 8001) -> ResearchMapAPIServer:
    """
    启动研究地图 API 服务器。

    Args:
        host: 监听主机
        port: 监听端口

    Returns:
        API 服务器实例
    """
    global _api_server

    if _api_server is None:
        _api_server = ResearchMapAPIServer(host=host, port=port)
        _api_server.start()

    return _api_server


def get_api_server() -> Optional[ResearchMapAPIServer]:
    """获取 API 服务器实例。"""
    return _api_server
