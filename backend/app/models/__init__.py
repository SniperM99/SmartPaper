"""数据模型定义"""
from app.models.requests import *
from app.models.responses import *

__all__ = [
    "PaperAnalysisRequest",
    "UrlAnalysisRequest",
    "PaperListResponse",
    "PaperDetailResponse",
    "AnalysisResultResponse",
    "ResearchMapQueryRequest",
    "ResearchMapResponse",
]
