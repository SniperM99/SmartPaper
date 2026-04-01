"""研究地图 API 路由"""
from fastapi import APIRouter, HTTPException

from app.models.requests import ResearchMapQueryRequest
from app.models.responses import ApiResponse
from app.services import ResearchMapService

router = APIRouter()
research_map_service = ResearchMapService()


@router.post("/query", response_model=ApiResponse)
async def query_research_map(request: ResearchMapQueryRequest):
    """查询研究地图

    支持自然语言查询论文相关问题
    """
    try:
        result = research_map_service.query(
            query=request.query,
            scope=request.scope,
            max_results=request.max_results,
        )

        return ApiResponse(
            success=True, message="查询成功", data=result
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data", response_model=ApiResponse)
async def get_map_data():
    """获取研究地图数据

    返回所有论文的知识图谱数据
    """
    try:
        result = research_map_service.get_map_data()

        return ApiResponse(
            success=result.get("success", False),
            message="获取成功" if result.get("success") else "获取失败",
            data=result.get("data"),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rebuild", response_model=ApiResponse)
async def rebuild_map():
    """重建研究地图

    基于论文库重新构建知识图谱
    """
    try:
        result = research_map_service.rebuild_map()

        return ApiResponse(
            success=result.get("success", False),
            message=result.get("message", "操作完成"),
            data=None,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
