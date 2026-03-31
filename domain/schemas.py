"""领域模型 - 统一输出 Schema 定义

用于统一规范和强类型化从 LLM 抽取的分析结构，确保下游知识图谱与数据库检索的一致性。
同时补充多源导入后的统一中间表示（NormalizedPaperSchema）。
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any


class EvidenceSchema(BaseModel):
    """证据引用片段"""
    claim: str = Field(..., description="所得出的结论或断言")
    section: str = Field(default="", description="结论来源的章节名称")
    text_span: str = Field(default="", description="原文中的原始文本片段")
    page: Optional[int] = Field(default=None, description="原文页码")


class QualityScoreSchema(BaseModel):
    """分析质量评分"""
    text_extraction: float = Field(default=0.0, ge=0.0, le=1.0, description="文本提取质量分数 (0-1)")
    section_detection: float = Field(default=0.0, ge=0.0, le=1.0, description="章节识别完整度 (0-1)")
    analysis_completeness: float = Field(default=0.0, ge=0.0, le=1.0, description="模型响应完整度 (0-1)")
    evidence_support: float = Field(default=0.0, ge=0.0, le=1.0, description="结论证据支撑度 (0-1)")
    overall_reliability: float = Field(default=0.0, ge=0.0, le=1.0, description="总体可信度评分 (0-1)")


class SourceSchema(BaseModel):
    """论文来源信息"""
    type: Literal["pdf", "url", "arxiv", "markdown", "text", "zotero_attachment", "zotero_item", "unknown"] = Field(default="unknown", description="来源类型")
    path: str = Field(default="", description="本地路径")
    url: str = Field(default="", description="在线链接")
    canonical_uri: str = Field(default="", description="统一后的主定位符")
    mime_type: str = Field(default="", description="MIME 类型")


class MetadataSchema(BaseModel):
    """论文元数据"""
    title: str = Field(default="", description="论文标题")
    authors: List[str] = Field(default_factory=list, description="作者列表")
    affiliations: List[str] = Field(default_factory=list, description="机构列表")
    year: str = Field(default="", description="发表年份")
    venue: str = Field(default="", description="发表期刊/会议")
    doi: str = Field(default="", description="DOI")
    keywords: List[str] = Field(default_factory=list, description="关键词")


class CitationSchema(BaseModel):
    """统一引用条目"""
    raw_text: str = Field(default="", description="原始引用文本")
    title: str = Field(default="", description="引用标题")
    authors: List[str] = Field(default_factory=list, description="作者列表")
    year: str = Field(default="", description="年份")
    venue: str = Field(default="", description="来源期刊/会议")
    doi: str = Field(default="", description="DOI")
    url: str = Field(default="", description="URL")


class AttachmentSchema(BaseModel):
    """附件信息"""
    name: str = Field(default="", description="附件名")
    type: Literal["pdf", "supplement", "dataset", "code", "image", "unknown"] = Field(default="unknown", description="附件类型")
    path: str = Field(default="", description="本地路径")
    url: str = Field(default="", description="在线链接")
    mime_type: str = Field(default="", description="MIME 类型")


class SectionSchema(BaseModel):
    """章节中间表示"""
    key: str = Field(default="", description="标准章节键")
    heading: str = Field(default="", description="原始或规范化标题")
    content: str = Field(default="", description="章节文本")
    word_count: int = Field(default=0, description="词数")


class ImportContextSchema(BaseModel):
    """导入上下文，用于 Zotero/未来多源扩展"""
    source_id: str = Field(default="", description="导入源唯一标识")
    parent_source_id: str = Field(default="", description="父对象标识，例如 Zotero 条目")
    zotero_item_key: str = Field(default="", description="Zotero item key")
    zotero_library_id: str = Field(default="", description="Zotero library id")
    collection_keys: List[str] = Field(default_factory=list, description="所属 collections")
    collection_paths: List[str] = Field(default_factory=list, description="所属 collections 路径")
    tags: List[str] = Field(default_factory=list, description="外部系统标签")
    attachment_keys: List[str] = Field(default_factory=list, description="外部附件 keys")
    analysis_refs: List[str] = Field(default_factory=list, description="关联分析结果引用")
    extra: Dict[str, Any] = Field(default_factory=dict, description="扩展字段")


class ZoteroTagSchema(BaseModel):
    """Zotero 标签"""
    name: str = Field(default="", description="标签名称")
    color: str = Field(default="", description="标签颜色")
    tag_type: str = Field(default="manual", description="标签类型")


class ZoteroCollectionSchema(BaseModel):
    """Zotero Collection"""
    key: str = Field(default="", description="Collection Key")
    name: str = Field(default="", description="Collection 名称")
    path: str = Field(default="", description="Collection 层级路径")
    parent_key: str = Field(default="", description="父 Collection Key")


class ZoteroAttachmentSchema(BaseModel):
    """Zotero 附件"""
    key: str = Field(default="", description="附件 Key")
    title: str = Field(default="", description="附件标题")
    content_type: str = Field(default="", description="附件 MIME 类型")
    link_mode: str = Field(default="", description="链接模式")
    path: str = Field(default="", description="附件路径")
    url: str = Field(default="", description="附件 URL")
    md5: str = Field(default="", description="附件 MD5")
    local_path: str = Field(default="", description="本地可访问路径")
    parent_item_key: str = Field(default="", description="父条目 Key")
    is_primary: bool = Field(default=False, description="是否为主 PDF")


class ZoteroLinkSchema(BaseModel):
    """Zotero 条目绑定信息"""
    library_id: str = Field(default="", description="Library ID")
    library_type: str = Field(default="user", description="Library 类型")
    item_key: str = Field(default="", description="条目 Key")
    version: Optional[int] = Field(default=None, description="远端版本")
    parent_item_key: str = Field(default="", description="父条目 Key")
    uri: str = Field(default="", description="Zotero URI")
    web_url: str = Field(default="", description="Web URL")


class SyncStateSchema(BaseModel):
    """同步状态"""
    provider: str = Field(default="zotero", description="外部系统")
    status: str = Field(default="pending", description="同步状态")
    direction: str = Field(default="import_only", description="同步方向")
    remote_version: Optional[int] = Field(default=None, description="远端版本")
    last_synced_version: Optional[int] = Field(default=None, description="本地最后同步版本")
    dedupe_fingerprint: str = Field(default="", description="去重/同步指纹")
    last_error: str = Field(default="", description="最近错误")


class LibraryContextSchema(BaseModel):
    """外部文献库上下文"""
    zotero: ZoteroLinkSchema = Field(default_factory=ZoteroLinkSchema)
    tags: List[ZoteroTagSchema] = Field(default_factory=list)
    collections: List[ZoteroCollectionSchema] = Field(default_factory=list)
    attachments: List[ZoteroAttachmentSchema] = Field(default_factory=list)
    sync_state: SyncStateSchema = Field(default_factory=SyncStateSchema)
    analysis_refs: List[str] = Field(default_factory=list)


class DocumentSchema(BaseModel):
    """论文内容摘要"""
    abstract: str = Field(default="", description="摘要文本")
    sections: List[str] = Field(default_factory=list, description="主要章节标题或简述")
    references: List[str] = Field(default_factory=list, description="核心引用的概要短文本")


class MethodSchema(BaseModel):
    """研究方法"""
    overview: str = Field(default="", description="方法论概述")
    steps: List[str] = Field(default_factory=list, description="执行步骤")
    inputs: List[str] = Field(default_factory=list, description="输入数据/依赖")
    outputs: List[str] = Field(default_factory=list, description="输出结果/目标")


class ExperimentsSchema(BaseModel):
    """实验设计与结果"""
    datasets: List[str] = Field(default_factory=list, description="数据集")
    metrics: List[str] = Field(default_factory=list, description="评估指标")
    baselines: List[str] = Field(default_factory=list, description="基线方法/对比标准")
    results: List[str] = Field(default_factory=list, description="实验核心结果概要")


class ReproducibilitySchema(BaseModel):
    """可复现性分析"""
    code_available: bool = Field(default=False, description="代码是否开源")
    data_available: bool = Field(default=False, description="数据是否开源")
    details: str = Field(default="", description="复现细节或仓库地址补充")


class AnalysisSchema(BaseModel):
    """论文深入分析"""
    summary_one_sentence: str = Field(default="", description="一句话总结(核心卖点)")
    research_problem: str = Field(default="", description="要解决的研究问题")
    background: str = Field(default="", description="研究背景与动机")
    method: MethodSchema = Field(default_factory=MethodSchema, description="研究方法细分")
    experiments: ExperimentsSchema = Field(default_factory=ExperimentsSchema, description="实验细节")
    contributions: List[str] = Field(default_factory=list, description="核心创新与贡献")
    innovation_points: List[str] = Field(default_factory=list, description="具体创新点列表")
    strengths: List[str] = Field(default_factory=list, description="论文优点")
    limitations: List[str] = Field(default_factory=list, description="方案局限性或缺陷")
    method_tags: List[str] = Field(default_factory=list, description="方法属性标签 (如: PIML, MPC)")
    dataset_tags: List[str] = Field(default_factory=list, description="数据集属性标签")
    application_tags: List[str] = Field(default_factory=list, description="应用场景标签")
    future_work: List[str] = Field(default_factory=list, description="未来研究方向")
    reproducibility: ReproducibilitySchema = Field(default_factory=ReproducibilitySchema, description="复现性判定")
    evidences: List[EvidenceSchema] = Field(default_factory=list, description="关键点证据绑定列表")
    topic_tags: List[str] = Field(default_factory=list, description="研究主题标签")


class TraceSchema(BaseModel):
    """分析执行追踪指标"""
    prompt_template: str = Field(default="", description="使用的 Prompt 模板名称")
    model_provider: str = Field(default="", description="使用的模型提供商")
    model_name: str = Field(default="", description="使用的模型名称")
    analysis_time: str = Field(default="", description="执行分析耗时(格式化字符串)")
    token_usage: Dict[str, Any] = Field(default_factory=dict, description="执行消耗的 Token 统计信息")


class StructuredAnalysisData(BaseModel):
    """全量标准化基础知识卡"""
    paper_id: str = Field(..., description="论文全局唯一 ID 或 Hash")
    source: SourceSchema = Field(default_factory=SourceSchema)
    metadata: MetadataSchema = Field(default_factory=MetadataSchema)
    document: DocumentSchema = Field(default_factory=DocumentSchema)
    analysis: AnalysisSchema = Field(default_factory=AnalysisSchema)
    citations: List[CitationSchema] = Field(default_factory=list, description="参考文献结构化条目")
    attachments: List[AttachmentSchema] = Field(default_factory=list, description="附件信息")
    import_context: ImportContextSchema = Field(default_factory=ImportContextSchema)
    library_context: LibraryContextSchema = Field(default_factory=LibraryContextSchema, description="外部文献库绑定与同步上下文")
    quality_control: QualityScoreSchema = Field(default_factory=QualityScoreSchema, description="分析质量预警与评分")
    trace: TraceSchema = Field(default_factory=TraceSchema)


class NormalizedPaperSchema(BaseModel):
    """多源统一导入后的中间表示"""
    paper_id: str = Field(..., description="统一 paper id")
    source: SourceSchema = Field(default_factory=SourceSchema)
    metadata: MetadataSchema = Field(default_factory=MetadataSchema)
    content: str = Field(default="", description="归一化后的全文文本")
    section_map: Dict[str, str] = Field(default_factory=dict, description="标准章节文本映射")
    sections: List[SectionSchema] = Field(default_factory=list, description="章节列表")
    citations: List[CitationSchema] = Field(default_factory=list, description="引用条目")
    attachments: List[AttachmentSchema] = Field(default_factory=list, description="附件条目")
    import_context: ImportContextSchema = Field(default_factory=ImportContextSchema)
    library_context: LibraryContextSchema = Field(default_factory=LibraryContextSchema, description="外部文献库绑定与同步上下文")
    document: DocumentSchema = Field(default_factory=DocumentSchema, description="面向知识卡的轻量文档视图")
