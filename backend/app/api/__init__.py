"""API 路由聚合"""
from fastapi import APIRouter

from app.api.routers import (
    paper_analysis,
    literature_ingestion,
    research_map,
    zotero,
    file_ops,
    profile,
    auth,
    admin,
)

# 创建主路由器
api_router = APIRouter()

# 注册各个路由
api_router.include_router(paper_analysis.router, prefix="/analysis", tags=["论文分析"])
api_router.include_router(literature_ingestion.router, prefix="/ingestion", tags=["文献导入"])
api_router.include_router(research_map.router, prefix="/research-map", tags=["研究地图"])
api_router.include_router(zotero.router, prefix="/zotero", tags=["Zotero集成"])
api_router.include_router(file_ops.router, prefix="/files", tags=["文件操作"])
api_router.include_router(profile.router, prefix="/profile", tags=["科研画像"])
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(admin.router, prefix="/admin", tags=["后台管理"])

__all__ = ["api_router"]
