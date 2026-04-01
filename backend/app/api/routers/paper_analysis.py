"""论文分析 API 路由"""
from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from typing import Generator
import json

from app.models.requests import (
    PaperAnalysisRequest,
    UrlAnalysisRequest,
    LocalPaperAnalysisRequest,
    MultiPaperComparisonRequest,
)
from app.models.responses import AnalysisResultResponse, ApiResponse
from app.services import AnalysisService

router = APIRouter()
analysis_service = AnalysisService()


def stream_generator(generator: Generator) -> Generator:
    """将生成器转换为 SSE 流式响应

    Args:
        generator: 数据生成器

    Yields:
        SSE 格式的数据
    """
    for chunk in generator:
        data = json.dumps(chunk, ensure_ascii=False)
        yield f"data: {data}\n\n"


@router.post("/analyze-file", response_model=ApiResponse)
async def analyze_file(
    file: UploadFile = File(...),
    role: str = Form(...),
    domain: str = Form(...),
    task: str = Form(...),
    use_chain: bool = Form(False),
):
    """上传并分析论文文件

    支持流式返回分析结果
    """
    try:
        # 保存上传的文件
        from app.services import FileService

        file_service = FileService()
        file_content = await file.read()

        saved_file = file_service.save_upload_file(file_content, file.filename)

        if saved_file["status"] != "uploaded":
            raise HTTPException(status_code=500, detail="文件保存失败")

        # 执行分析
        return StreamingResponse(
            stream_generator(
                analysis_service.analyze_from_file(
                    file_path=saved_file["path"],
                    role=role,
                    task=task,
                    domain=domain,
                    use_chain=use_chain,
                )
            ),
            media_type="text/event-stream",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-url")
async def analyze_url(request: UrlAnalysisRequest):
    """从 URL 分析论文

    支持流式返回分析结果
    """
    try:
        return StreamingResponse(
            stream_generator(
                analysis_service.analyze_from_url(
                    url=request.url,
                    role=request.role,
                    task=request.task,
                    domain=request.domain,
                    use_chain=request.use_chain,
                )
            ),
            media_type="text/event-stream",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-local")
async def analyze_local(request: LocalPaperAnalysisRequest):
    """分析本地论文文件

    支持流式返回分析结果
    """
    try:
        return StreamingResponse(
            stream_generator(
                analysis_service.analyze_from_file(
                    file_path=request.file_path,
                    role=request.role,
                    task=request.task,
                    domain=request.domain,
                    use_chain=request.use_chain,
                )
            ),
            media_type="text/event-stream",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_papers(request: MultiPaperComparisonRequest):
    """多论文对比分析

    支持流式返回分析结果
    """
    try:
        return StreamingResponse(
            stream_generator(
                analysis_service.compare_papers(
                    main_paper_id=request.main_paper_id,
                    compare_paper_ids=request.compare_paper_ids,
                    role=request.role,
                    domain=request.domain,
                    task=request.task,
                )
            ),
            media_type="text/event-stream",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/result/{paper_id}", response_model=ApiResponse)
async def get_analysis_result(paper_id: str):
    """获取论文分析结果

    Args:
        paper_id: 论文ID

    Returns:
        分析结果
    """
    try:
        # TODO: 从数据库或文件系统获取分析结果
        result = {}

        return ApiResponse(success=True, message="获取成功", data=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
