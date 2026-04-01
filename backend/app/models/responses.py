"""响应数据模型"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal


class ApiResponse(BaseModel):
    """统一API响应格式"""

    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")


class PaperListResponse(BaseModel):
    """论文列表响应"""

    total: int = Field(..., description="论文总数")
    papers: List[Dict[str, Any]] = Field(..., description="论文列表")


class PaperDetailResponse(BaseModel):
    """论文详情响应"""

    paper_id: str = Field(..., description="论文ID")
    title: str = Field(..., description="标题")
    authors: List[str] = Field(..., description="作者列表")
    abstract: Optional[str] = Field(None, description="摘要")
    metadata: Dict[str, Any] = Field(..., description="元数据")
    parsed_content: Optional[Dict[str, Any]] = Field(None, description="解析内容")
    analysis_result: Optional[Dict[str, Any]] = Field(None, description="分析结果")
    quality_scores: Optional[Dict[str, float]] = Field(None, description="质量评分")
    created_at: str = Field(..., description="创建时间")
    source: str = Field(..., description="来源: upload|url|local|zotero")


class AnalysisStreamChunk(BaseModel):
    """分析流式响应数据块"""

    type: Literal["chunk", "final", "error"] = Field(..., description="数据块类型")
    content: Optional[str] = Field(None, description="内容块（type=chunk）")
    success: Optional[bool] = Field(None, description="是否成功（type=final）")
    file_path: Optional[str] = Field(None, description="输出文件路径（type=final）")
    error: Optional[str] = Field(None, description="错误信息（type=error）")
    paper_id: Optional[str] = Field(None, description="论文ID（type=final）")


class AnalysisResultResponse(BaseModel):
    """分析结果响应"""

    paper_id: str = Field(..., description="论文ID")
    title: str = Field(..., description="标题")
    status: str = Field(..., description="状态: pending|processing|completed|failed")
    result: Optional[Dict[str, Any]] = Field(None, description="分析结果")
    quality_scores: Optional[Dict[str, float]] = Field(None, description="质量评分")
    file_path: Optional[str] = Field(None, description="输出文件路径")
    error: Optional[str] = Field(None, description="错误信息")
    created_at: str = Field(..., description="创建时间")
    completed_at: Optional[str] = Field(None, description="完成时间")


class IngestionTaskResponse(BaseModel):
    """导入任务响应"""

    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="状态: pending|processing|completed|failed")
    total: int = Field(..., description="总数")
    processed: int = Field(..., description="已处理数")
    failed: int = Field(..., description="失败数")
    results: List[Dict[str, Any]] = Field(..., description="结果列表")
    error: Optional[str] = Field(None, description="错误信息")


class ResearchMapResponse(BaseModel):
    """研究地图响应"""

    query: str = Field(..., description="查询内容")
    answer: str = Field(..., description="回答内容")
    sources: List[Dict[str, Any]] = Field(..., description="来源论文列表")
    reasoning: Optional[str] = Field(None, description="推理过程")


class ZoteroCollectionResponse(BaseModel):
    """Zotero 收藏夹响应"""

    collections: List[Dict[str, Any]] = Field(..., description="收藏夹列表")


class ZoteroItemsResponse(BaseModel):
    """Zotero 文献条目响应"""

    items: List[Dict[str, Any]] = Field(..., description="文献条目列表")
    total: int = Field(..., description="总数")


class FileUploadResponse(BaseModel):
    """文件上传响应"""

    file_id: str = Field(..., description="文件ID")
    filename: str = Field(..., description="文件名")
    size: int = Field(..., description="文件大小（字节）")
    path: str = Field(..., description="存储路径")
    status: str = Field(..., description="状态: uploaded|failed")


class HealthResponse(BaseModel):
    """健康检查响应"""

    service: str = Field(..., description="服务名称")
    status: str = Field(..., description="状态")
    version: str = Field(..., description="版本")


class ProfileResponse(BaseModel):
    """科研画像响应"""

    user_context: Dict[str, Any] = Field(..., description="用户上下文")
    interests: List[str] = Field(..., description="关注关键词")
    analysis_focus: List[str] = Field(..., description="分析侧重")
    updated_at: str = Field(..., description="更新时间")


class AnalysisOptionsResponse(BaseModel):
    """分析选项响应"""

    roles: Dict[str, str] = Field(..., description="角色选项")
    domains: Dict[str, str] = Field(..., description="领域选项")
    tasks: Dict[str, str] = Field(..., description="任务选项")
    prompts: Dict[str, str] = Field(..., description="提示词预设")
