"""研究地图 API 接口定义。"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ResearchMapRequest(BaseModel):
    """研究地图请求。"""

    cache_keys: List[str] = Field(default_factory=list, description="知识卡缓存键列表")


class ResearchMapResponse(BaseModel):
    """研究地图响应。"""

    data: Dict[str, Any] = Field(..., description="研究地图数据")
    status: str = Field(default="success", description="状态")


class EntityDetailRequest(BaseModel):
    """实体详情请求。"""

    entity_id: str = Field(..., description="实体 ID")


class EntityDetailResponse(BaseModel):
    """实体详情响应。"""

    entity: Dict[str, Any] = Field(..., description="实体详情")
    related_papers: List[Dict[str, Any]] = Field(default_factory=list, description="相关论文")
    relations: List[Dict[str, Any]] = Field(default_factory=list, description="关系列表")


class SearchRequest(BaseModel):
    """搜索请求。"""

    query: str = Field(..., description="搜索关键词")
    entity_types: Optional[List[str]] = Field(default=None, description="实体类型过滤")
    min_mentions: Optional[int] = Field(default=None, description="最小提及数")


class SearchResponse(BaseModel):
    """搜索响应。"""

    results: List[Dict[str, Any]] = Field(..., description="搜索结果")
    total: int = Field(..., description="总数")


class ExportRequest(BaseModel):
    """导出请求。"""

    format: str = Field(default="json", description="导出格式：json/svg")
    cache_keys: List[str] = Field(default_factory=list, description="知识卡缓存键列表")
