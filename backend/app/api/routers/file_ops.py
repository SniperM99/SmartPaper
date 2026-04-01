"""文件操作 API 路由"""
from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from typing import Optional

from app.models.responses import ApiResponse, FileUploadResponse
from app.services import FileService

router = APIRouter()
file_service = FileService()


@router.post("/upload", response_model=ApiResponse)
async def upload_file(file: UploadFile = File(...)):
    """上传文件

    支持任意类型文件上传
    """
    try:
        file_content = await file.read()
        result = file_service.save_upload_file(file_content, file.filename)

        if result["status"] != "uploaded":
            raise HTTPException(status_code=500, detail="文件上传失败")

        return ApiResponse(
            success=True,
            message="文件上传成功",
            data=result,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{file_path:path}")
async def download_file(file_path: str):
    """下载文件

    Args:
        file_path: 文件路径
    """
    try:
        from pathlib import Path

        path = Path(file_path)

        if not path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")

        return FileResponse(
            path=path,
            filename=path.name,
            media_type="application/octet-stream",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream/{file_path:path}")
async def stream_file(file_path: str):
    """流式读取文件

    Args:
        file_path: 文件路径
    """
    try:
        return StreamingResponse(
            file_service.get_file(file_path),
            media_type="application/octet-stream",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info/{file_path:path}", response_model=ApiResponse)
async def get_file_info(file_path: str):
    """获取文件信息

    Args:
        file_path: 文件路径
    """
    try:
        info = file_service.get_file_info(file_path)

        return ApiResponse(
            success=info.get("exists", False),
            message="获取成功" if info.get("exists") else "文件不存在",
            data=info,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{file_path:path}", response_model=ApiResponse)
async def delete_file(file_path: str):
    """删除文件

    Args:
        file_path: 文件路径
    """
    try:
        success = file_service.delete_file(file_path)

        return ApiResponse(
            success=success,
            message="文件已删除" if success else "文件不存在",
            data={"path": file_path},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
