"""研究地图到 UI 图谱展示的稳定视图 DTO。"""

from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field


GraphNodeKind = Literal["paper", "topic", "problem", "method", "dataset", "metric", "gap"]
GraphEdgeKind = Literal[
    "studies_topic",
    "addresses_problem",
    "uses_method",
    "evaluates_on_dataset",
    "evaluated_by_metric",
    "related_to",
    "evolves_from",
    "highlights_gap",
]
GraphLayoutHint = Literal["force", "timeline", "cluster", "radial"]
GraphState = Literal["ready", "empty", "degraded", "failed"]


class AnalysisRefSchema(BaseModel):
    """图谱节点关联的分析引用。"""

    ref_id: str = Field(default="", description="分析引用 ID，如 cache_key 或 analysis result id")
    ref_type: Literal["knowledge_card", "analysis_result", "history_cache"] = Field(
        default="knowledge_card", description="引用类型"
    )
    label: str = Field(default="", description="展示标签")


class GraphNodeViewSchema(BaseModel):
    """UI 图谱节点视图模型。"""

    id: str = Field(..., description="节点唯一 ID，对应 research map entity id")
    kind: GraphNodeKind = Field(..., description="节点类别")
    label: str = Field(..., description="节点名称")
    subtitle: str = Field(default="", description="节点副标题，例如 topic · 3 papers")
    size: int = Field(default=1, ge=1, description="推荐节点大小")
    color_token: str = Field(default="default", description="前端主题色 token")
    paper_ids: List[str] = Field(default_factory=list, description="关联论文 ID")
    tags: List[str] = Field(default_factory=list, description="可用于筛选/高亮的标签")
    collections: List[str] = Field(default_factory=list, description="关联 collection path 或 key")
    analysis_refs: List[AnalysisRefSchema] = Field(default_factory=list, description="关联分析结果引用")
    badges: List[str] = Field(default_factory=list, description="前端可直接显示的徽标文本")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="附加展示信息")


class GraphEdgeViewSchema(BaseModel):
    """UI 图谱边视图模型。"""

    id: str = Field(..., description="边唯一 ID")
    kind: GraphEdgeKind = Field(..., description="边类型")
    source: str = Field(..., description="源节点 ID")
    target: str = Field(..., description="目标节点 ID")
    label: str = Field(default="", description="边标签")
    weight: float = Field(default=1.0, ge=0.0, description="边权重")
    paper_ids: List[str] = Field(default_factory=list, description="支持该边的论文 ID")
    analysis_refs: List[AnalysisRefSchema] = Field(default_factory=list, description="关联分析结果引用")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="共享实体、年份跨度等展示信息")


class GraphLegendItemSchema(BaseModel):
    """图例项。"""

    key: str = Field(..., description="图例键")
    label: str = Field(..., description="图例展示名称")
    color_token: str = Field(default="default", description="色彩 token")
    shape: str = Field(default="circle", description="图形形状建议")


class GraphEmptyStateSchema(BaseModel):
    """空态/退化态建议。"""

    state: GraphState = Field(default="ready", description="当前图谱状态")
    title: str = Field(default="", description="空态标题")
    description: str = Field(default="", description="说明文案")
    suggestions: List[str] = Field(default_factory=list, description="建议动作")


class ResearchMapGraphViewSchema(BaseModel):
    """工作台图谱展示的统一视图 DTO。"""

    map_id: str = Field(default="", description="研究地图 ID 或查询 scope id")
    state: GraphState = Field(default="ready", description="视图状态")
    layout_hint: GraphLayoutHint = Field(default="force", description="布局建议")
    nodes: List[GraphNodeViewSchema] = Field(default_factory=list, description="节点列表")
    edges: List[GraphEdgeViewSchema] = Field(default_factory=list, description="边列表")
    legend: List[GraphLegendItemSchema] = Field(default_factory=list, description="图例")
    empty_state: GraphEmptyStateSchema = Field(default_factory=GraphEmptyStateSchema, description="空态/退化态")
    filters_applied: Dict[str, Any] = Field(default_factory=dict, description="当前已应用过滤条件")
    stats: Dict[str, Any] = Field(default_factory=dict, description="供 UI 顶部摘要卡使用的统计")
