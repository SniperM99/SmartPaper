"""科研画像 API 路由"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional

from app.models.requests import ProfileUpdateRequest
from app.models.responses import ApiResponse, ProfileResponse, AnalysisOptionsResponse
from app.services import ProfileService

router = APIRouter()
profile_service = ProfileService()


@router.get("/profile", response_model=ApiResponse)
async def get_profile():
    """获取科研画像

    返回当前用户的科研背景、关注点等信息
    """
    try:
        profile = profile_service.get_profile()

        return ApiResponse(
            success=True,
            message="获取成功",
            data=profile,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/profile", response_model=ApiResponse)
async def update_profile(request: ProfileUpdateRequest):
    """更新科研画像

    支持更新角色、研究领域、课题、关键词等
    """
    try:
        result = profile_service.update_profile(
            role=request.role,
            research_area=request.research_area,
            current_project=request.current_project,
            interests=request.interests,
            analysis_focus=request.analysis_focus,
        )

        return ApiResponse(
            success=result.get("success", False),
            message=result.get("message", "更新完成"),
            data=result.get("profile"),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/options", response_model=ApiResponse)
async def get_analysis_options():
    """获取分析选项

    返回可用的角色、领域、任务和提示词预设
    """
    try:
        options = profile_service.get_analysis_options()

        return ApiResponse(
            success=True,
            message="获取成功",
            data=options,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
