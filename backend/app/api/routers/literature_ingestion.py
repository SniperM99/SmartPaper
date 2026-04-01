"""文献导入 API 路由"""
from fastapi import APIRouter, HTTPException
from typing import List

from app.models.requests import BatchIngestionRequest, ArxivDownloadRequest
from app.models.responses import ApiResponse, PaperListResponse, PaperDetailResponse
from app.services import IngestionService

router = APIRouter()
ingestion_service = IngestionService()


@router.post("/ingest-local", response_model=ApiResponse)
async def ingest_local_paths(request: BatchIngestionRequest):
    """批量导入本地文献

    支持文件或文件夹路径
    """
    try:
        result = ingestion_service.ingest_local_paths(
            paths=request.paths, recursive=request.recursive
        )

        return ApiResponse(
            success=result["status"] == "completed",
            message=f"导入完成: 成功 {result['processed']}，失败 {result['failed']}",
            data=result,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest-arxiv", response_model=ApiResponse)
async def ingest_from_arxiv(request: ArxivDownloadRequest):
    """从 arXiv 下载并导入文献"""
    try:
        result = ingestion_service.ingest_from_arxiv(arxiv_ids=request.arxiv_ids)

        return ApiResponse(
            success=result["status"] == "completed",
            message=f"下载完成: 成功 {result['processed']}，失败 {result['failed']}",
            data=result,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/papers", response_model=ApiResponse)
async def get_papers():
    """获取论文库列表"""
    try:
        papers = ingestion_service.get_paper_list()

        return ApiResponse(
            success=True,
            message="获取成功",
            data={
                "total": len(papers),
                "papers": papers,
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/papers/{paper_id}", response_model=ApiResponse)
async def get_paper(paper_id: str):
    """获取论文详情

    Args:
        paper_id: 论文ID
    """
    try:
        paper = ingestion_service.get_paper_detail(paper_id)

        if not paper:
            raise HTTPException(status_code=404, detail="论文不存在")

        return ApiResponse(success=True, message="获取成功", data=paper)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/papers/{paper_id}", response_model=ApiResponse)
async def delete_paper(paper_id: str):
    """删除论文

    Args:
        paper_id: 论文ID
    """
    try:
        result = ingestion_service.delete_paper(paper_id)

        return ApiResponse(success=True, message="论文已删除", data=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
