"""Zotero 集成 API 路由"""
from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional

from app.models.responses import ApiResponse
from app.services import ZoteroService

router = APIRouter()
zotero_service = ZoteroService()


@router.get("/collections", response_model=ApiResponse)
async def get_collections():
    """获取 Zotero 收藏夹列表"""
    try:
        collections = zotero_service.get_collections()

        return ApiResponse(
            success=True,
            message=f"获取到 {len(collections)} 个收藏夹",
            data={"collections": collections},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/items", response_model=ApiResponse)
async def get_items(collection_id: Optional[str] = None, limit: int = 50):
    """获取 Zotero 文献条目

    Args:
        collection_id: 收藏夹ID，不指定则获取全部
        limit: 限制数量
    """
    try:
        result = zotero_service.get_items(
            collection_id=collection_id, limit=limit
        )

        return ApiResponse(
            success=True,
            message=f"获取到 {result['total']} 个文献条目",
            data=result,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import", response_model=ApiResponse)
async def import_items(
    item_keys: List[str] = Body(..., embed=True),
    analysis_config: Optional[dict] = Body(None, embed=True),
):
    """从 Zotero 导入文献到 SmartPaper

    Args:
        item_keys: 文献条目key列表
        analysis_config: 分析配置（可选）
    """
    try:
        result = zotero_service.import_items(
            item_keys=item_keys, analysis_config=analysis_config
        )

        return ApiResponse(
            success=result["status"] == "completed",
            message=f"导入完成: 成功 {result['processed']}，失败 {result['failed']}",
            data=result,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-connection", response_model=ApiResponse)
async def test_connection():
    """测试 Zotero 连接"""
    try:
        result = zotero_service.test_connection()

        return ApiResponse(
            success=result["success"],
            message=result["message"],
            data={"user_id": result.get("user_id", "")},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
