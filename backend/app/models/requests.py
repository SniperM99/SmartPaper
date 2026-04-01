"""请求数据模型"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any


class PaperAnalysisRequest(BaseModel):
    """论文分析请求"""

    role: str = Field(..., description="分析角色", example="phd_assistant")
    domain: str = Field(..., description="研究领域", example="general")
    task: str = Field(..., description="分析任务", example="phd_analysis")
    use_chain: bool = Field(False, description="是否开启多轮分析链")
    paper_id: Optional[str] = Field(None, description="论文ID（从论文库选择）")


class UrlAnalysisRequest(BaseModel):
    """URL分析请求"""

    url: str = Field(..., description="arXiv或其他论文URL", example="https://arxiv.org/abs/2310.12345")
    role: str = Field(..., description="分析角色", example="phd_assistant")
    domain: str = Field(..., description="研究领域", example="general")
    task: str = Field(..., description="分析任务", example="phd_analysis")
    use_chain: bool = Field(False, description="是否开启多轮分析链")


class LocalPaperAnalysisRequest(BaseModel):
    """本地论文分析请求"""

    file_path: str = Field(..., description="本地文件路径")
    role: str = Field(..., description="分析角色", example="phd_assistant")
    domain: str = Field(..., description="研究领域", example="general")
    task: str = Field(..., description="分析任务", example="phd_analysis")
    use_chain: bool = Field(False, description="是否开启多轮分析链")


class MultiPaperComparisonRequest(BaseModel):
    """多论文对比分析请求"""

    main_paper_id: str = Field(..., description="主论文ID")
    compare_paper_ids: List[str] = Field(..., description="对比论文ID列表", min_length=1, max_length=5)
    role: str = Field(..., description="分析角色", example="phd_assistant")
    domain: str = Field(..., description="研究领域", example="general")
    task: str = Field(..., description="分析任务", example="cross_paper_comparison")


class BatchIngestionRequest(BaseModel):
    """批量导入请求"""

    paths: List[str] = Field(..., description="文件或文件夹路径列表")
    recursive: bool = Field(False, description="是否递归扫描子文件夹")


class ArxivDownloadRequest(BaseModel):
    """arXiv 下载请求"""

    arxiv_ids: List[str] = Field(..., description="arXiv ID列表", example=["2310.12345", "2311.54321"])


class ZoteroSyncRequest(BaseModel):
    """Zotero 同步请求"""

    collection_id: Optional[str] = Field(None, description="指定收藏夹ID，不指定则同步全部")
    since_version: Optional[int] = Field(None, description="从指定版本开始同步")


class ResearchMapQueryRequest(BaseModel):
    """研究地图查询请求"""

    query: str = Field(..., description="自然语言查询", example="transformer 架构有哪些创新点？")
    scope: str = Field("all", description="查询范围: all|active|compare")
    max_results: int = Field(5, description="最大结果数")


class FileUploadRequest(BaseModel):
    """文件上传请求"""

    analysis_config: Optional[Dict[str, Any]] = Field(
        None,
        description="分析配置",
        example={"role": "phd_assistant", "domain": "general", "task": "phd_analysis"},
    )


class ProfileUpdateRequest(BaseModel):
    """科研画像更新请求"""

    role: Optional[str] = Field(None, description="身份/角色")
    research_area: Optional[str] = Field(None, description="研究领域")
    current_project: Optional[str] = Field(None, description="当前课题")
    interests: Optional[List[str]] = Field(None, description="关注关键词")
    analysis_focus: Optional[List[str]] = Field(None, description="分析侧重")
