"""研究地图 Schema 定义。

围绕结构化知识卡，定义研究地图最小可用实体、关系、时间线、聚类与研究空白结构。
"""

from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field


EntityType = Literal["paper", "topic", "problem", "method", "dataset", "metric", "gap"]
RelationType = Literal[
    "studies_topic",
    "addresses_problem",
    "uses_method",
    "evaluates_on_dataset",
    "evaluated_by_metric",
    "related_to",
    "evolves_from",
    "highlights_gap",
]


class ResearchEntitySchema(BaseModel):
    """研究地图实体节点。"""

    id: str = Field(..., description="全局唯一节点 ID")
    entity_type: EntityType = Field(..., description="实体类型")
    label: str = Field(..., description="展示名称")
    aliases: List[str] = Field(default_factory=list, description="别名或原始候选名")
    paper_ids: List[str] = Field(default_factory=list, description="关联论文 ID 列表")
    mentions: int = Field(default=0, description="在样本中出现的次数")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="附加元数据")


class ResearchRelationSchema(BaseModel):
    """研究地图边。"""

    source: str = Field(..., description="源节点 ID")
    target: str = Field(..., description="目标节点 ID")
    relation_type: RelationType = Field(..., description="关系类型")
    weight: float = Field(default=1.0, description="关系强度")
    evidence_paper_ids: List[str] = Field(default_factory=list, description="支持该关系的论文 ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="附加信息，如共享实体、年份跨度")


class ResearchTimelineEventSchema(BaseModel):
    """年度时间线事件。"""

    year: str = Field(default="unknown", description="年份")
    paper_ids: List[str] = Field(default_factory=list, description="该年份论文 ID")
    key_topics: List[str] = Field(default_factory=list, description="该年份高频主题")
    key_methods: List[str] = Field(default_factory=list, description="该年份高频方法")
    highlights: List[str] = Field(default_factory=list, description="年度摘要")


class ResearchClusterSchema(BaseModel):
    """研究簇。"""

    id: str = Field(..., description="聚类 ID")
    label: str = Field(..., description="簇标签")
    paper_ids: List[str] = Field(default_factory=list, description="簇内论文 ID")
    topic_ids: List[str] = Field(default_factory=list, description="簇覆盖主题 ID")
    method_ids: List[str] = Field(default_factory=list, description="簇覆盖方法 ID")
    summary: str = Field(default="", description="簇摘要")


class ResearchGapSchema(BaseModel):
    """研究空白或候选机会点。"""

    id: str = Field(..., description="空白 ID")
    title: str = Field(..., description="空白标题")
    description: str = Field(default="", description="空白说明")
    gap_type: Literal["explicit_gap", "sparse_topic", "missing_evaluation"] = Field(
        ..., description="空白类型"
    )
    priority: Literal["high", "medium", "low"] = Field(default="medium", description="优先级")
    evidence_paper_ids: List[str] = Field(default_factory=list, description="支持空白的论文 ID")
    related_entity_ids: List[str] = Field(default_factory=list, description="相关主题/方法/指标等节点 ID")


class ResearchMapSchema(BaseModel):
    """研究地图整体输出。"""

    overview: Dict[str, Any] = Field(default_factory=dict, description="总体统计信息")
    entities: List[ResearchEntitySchema] = Field(default_factory=list, description="全部节点")
    relations: List[ResearchRelationSchema] = Field(default_factory=list, description="全部边")
    timeline: List[ResearchTimelineEventSchema] = Field(default_factory=list, description="时间线")
    clusters: List[ResearchClusterSchema] = Field(default_factory=list, description="研究簇")
    gaps: List[ResearchGapSchema] = Field(default_factory=list, description="研究空白")
