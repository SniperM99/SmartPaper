"""研究地图查询 DTO 与检索接口草案。"""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


SortOrder = Literal["asc", "desc"]
ResearchMapView = Literal["graph", "timeline", "gaps", "entities", "relations", "export"]
EntitySortField = Literal["label", "mentions", "entity_type"]
RelationSortField = Literal["weight", "relation_type"]
GapSortField = Literal["priority", "title"]
TimelineSortField = Literal["year"]
ExportFormat = Literal["json", "jsonl", "csv", "markdown"]


class ResearchMapQueryScope(BaseModel):
    """查询范围。"""

    map_id: str = Field(default="", description="研究地图 ID；为空表示动态按条件构建/查询")
    paper_ids: List[str] = Field(default_factory=list, description="限制到指定论文集合")
    source: Literal["ready_cards", "legacy_structured_data", "mixed"] = Field(
        default="ready_cards", description="查询源范围"
    )


class ResearchMapQueryFilters(BaseModel):
    """统一过滤条件。"""

    text_query: str = Field(default="", description="模糊检索词，匹配 label/title/description")
    entity_types: List[str] = Field(default_factory=list, description="实体类型过滤")
    relation_types: List[str] = Field(default_factory=list, description="关系类型过滤")
    years: List[str] = Field(default_factory=list, description="年份过滤；可包含 unknown")
    topic_labels: List[str] = Field(default_factory=list, description="主题标签过滤")
    method_labels: List[str] = Field(default_factory=list, description="方法标签过滤")
    gap_types: List[str] = Field(default_factory=list, description="空白类型过滤")
    priorities: List[str] = Field(default_factory=list, description="空白优先级过滤")
    paper_ids: List[str] = Field(default_factory=list, description="只看与这些 paper_id 相关的结果")
    include_isolated_nodes: bool = Field(default=False, description="graph 视图是否保留孤立节点")
    min_mentions: int = Field(default=0, ge=0, description="节点最少出现次数")
    min_relation_weight: float = Field(default=0.0, ge=0.0, description="边最小权重")


class PaginationSchema(BaseModel):
    """分页语义。"""

    page: int = Field(default=1, ge=1, description="页码，从 1 开始")
    page_size: int = Field(default=20, ge=1, le=200, description="每页数量")


class SortSchema(BaseModel):
    """排序语义。"""

    sort_by: str = Field(default="label", description="排序字段，具体视图决定允许值")
    sort_order: SortOrder = Field(default="asc", description="排序方向")


class ResearchMapQueryRequest(BaseModel):
    """研究地图统一查询请求。"""

    scope: ResearchMapQueryScope = Field(default_factory=ResearchMapQueryScope)
    view: ResearchMapView = Field(default="graph", description="查询视图")
    filters: ResearchMapQueryFilters = Field(default_factory=ResearchMapQueryFilters)
    pagination: PaginationSchema = Field(default_factory=PaginationSchema)
    sort: SortSchema = Field(default_factory=SortSchema)
    include_fields: List[str] = Field(default_factory=list, description="可选字段投影")


class ResearchMapListItem(BaseModel):
    """列表项的统一包装。"""

    item_type: Literal["entity", "relation", "timeline", "gap"] = Field(..., description="项类型")
    id: str = Field(..., description="项 ID")
    title: str = Field(default="", description="标题或主标签")
    subtitle: str = Field(default="", description="补充说明")
    paper_ids: List[str] = Field(default_factory=list, description="关联论文")
    sort_value: str = Field(default="", description="用于前端显示当前排序键")
    payload: Dict[str, Any] = Field(default_factory=dict, description="原始结构化负载")


class PageInfoSchema(BaseModel):
    """分页信息。"""

    page: int = Field(default=1)
    page_size: int = Field(default=20)
    total: int = Field(default=0)
    returned: int = Field(default=0)
    has_next: bool = Field(default=False)


class ResearchMapQueryResponse(BaseModel):
    """研究地图查询响应。"""

    scope: ResearchMapQueryScope = Field(default_factory=ResearchMapQueryScope)
    view: ResearchMapView = Field(default="graph")
    filters: ResearchMapQueryFilters = Field(default_factory=ResearchMapQueryFilters)
    sort: SortSchema = Field(default_factory=SortSchema)
    page_info: PageInfoSchema = Field(default_factory=PageInfoSchema)
    items: List[ResearchMapListItem] = Field(default_factory=list, description="当前页结果")
    aggregations: Dict[str, Any] = Field(default_factory=dict, description="facet/统计信息")


class ResearchMapExportRequest(BaseModel):
    """研究地图导出请求。"""

    query: ResearchMapQueryRequest = Field(default_factory=ResearchMapQueryRequest)
    export_format: ExportFormat = Field(default="json", description="导出格式")
    flatten: bool = Field(default=False, description="是否展平为扁平记录")


class ResearchMapExportResponse(BaseModel):
    """研究地图导出响应描述。"""

    export_format: ExportFormat = Field(default="json")
    file_name: str = Field(default="research_map_export.json")
    content_type: str = Field(default="application/json")
    record_count: int = Field(default=0)
    content: str = Field(default="", description="序列化内容或下载引用")


class ResearchMapQueryServiceDraft(BaseModel):
    """仅用于文档化的最小接口草案。"""

    list_entities: str = Field(default="list_entities(request: ResearchMapQueryRequest) -> ResearchMapQueryResponse")
    list_relations: str = Field(default="list_relations(request: ResearchMapQueryRequest) -> ResearchMapQueryResponse")
    list_timeline: str = Field(default="list_timeline(request: ResearchMapQueryRequest) -> ResearchMapQueryResponse")
    list_gaps: str = Field(default="list_gaps(request: ResearchMapQueryRequest) -> ResearchMapQueryResponse")
    export_map: str = Field(default="export_map(request: ResearchMapExportRequest) -> ResearchMapExportResponse")
