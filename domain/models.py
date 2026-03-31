"""领域模型定义

定义核心业务对象：论文、分析结果、引用等
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import hashlib


class AnalysisStatus(Enum):
    """分析任务状态"""
    PENDING = "pending"
    PARSING = "parsing"
    ANALYZING = "analyzing"
    SUMMARIZING = "summarizing"
    COMPLETED = "completed"
    FAILED = "failed"


class SyncStatus(Enum):
    """外部系统同步状态"""
    PENDING = "pending"
    SYNCED = "synced"
    DIRTY_LOCAL = "dirty_local"
    DIRTY_REMOTE = "dirty_remote"
    CONFLICT = "conflict"
    ERROR = "error"


class SyncDirection(Enum):
    """同步方向"""
    IMPORT_ONLY = "import_only"
    EXPORT_ANALYSIS = "export_analysis"
    BIDIRECTIONAL = "bidirectional"


class PromptTemplate(Enum):
    """提示词模板类型"""
    YUANBAO = "yuanbao"
    COOLPAPERS = "coolpapaers"
    METHODOLOGY = "methodology"
    RESULTS = "results"
    CONTRIBUTION = "contribution"
    FULL_ANALYSIS = "full_analysis"
    PHD_ANALYSIS = "phd_analysis"
    TEST_ANALYSIS = "test_analysis"


@dataclass
class PaperMetadata:
    """论文元数据"""
    title: str
    authors: List[str] = field(default_factory=list)
    abstract: Optional[str] = None
    journal: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    file_path: Optional[str] = None
    file_hash: Optional[str] = None
    file_size: Optional[int] = None
    page_count: Optional[int] = None
    keywords: List[str] = field(default_factory=list)
    references: List["ReferenceItem"] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PaperMetadata":
        """从字典创建元数据"""
        return cls(
            title=data.get("title", ""),
            authors=data.get("authors", []),
            abstract=data.get("abstract"),
            journal=data.get("journal"),
            year=data.get("year"),
            doi=data.get("doi"),
            url=data.get("url"),
            file_path=data.get("file_path"),
            file_hash=data.get("file_hash"),
            file_size=data.get("file_size"),
            page_count=data.get("page_count"),
            keywords=data.get("keywords", []),
            references=[ReferenceItem.from_dict(r) for r in data.get("references", [])],
            extra=data.get("extra", {}),
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "journal": self.journal,
            "year": self.year,
            "doi": self.doi,
            "url": self.url,
            "file_path": self.file_path,
            "file_hash": self.file_hash,
            "file_size": self.file_size,
            "page_count": self.page_count,
            "keywords": self.keywords,
            "references": [r.to_dict() for r in self.references],
            "extra": self.extra,
        }


@dataclass
class PaperSection:
    """论文章节"""
    title: str
    content: str
    section_type: str = "section"
    level: int = 1
    page_start: Optional[int] = None
    page_end: Optional[int] = None


@dataclass
class ReferenceItem:
    """参考文献条目"""
    title: str
    authors: List[str] = field(default_factory=list)
    journal: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    citation_text: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReferenceItem":
        """从字典创建引用"""
        return cls(
            title=data.get("title", ""),
            authors=data.get("authors", []),
            journal=data.get("journal"),
            year=data.get("year"),
            doi=data.get("doi"),
            url=data.get("url"),
            citation_text=data.get("citation_text"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "title": self.title,
            "authors": self.authors,
            "journal": self.journal,
            "year": self.year,
            "doi": self.doi,
            "url": self.url,
            "citation_text": self.citation_text,
        }


@dataclass
class PaperDocument:
    """论文文档 - 领域核心对象"""
    id: str
    metadata: PaperMetadata
    content: str
    sections: List[PaperSection] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    @classmethod
    def create(cls, content: str, metadata: Optional[Dict[str, Any]] = None) -> "PaperDocument":
        """创建论文文档"""
        metadata = metadata or {}
        doc_id = hashlib.md5(content.encode()).hexdigest()[:16]
        
        return cls(
            id=doc_id,
            metadata=PaperMetadata.from_dict(metadata),
            content=content,
        )

    def update_content(self, content: str):
        """更新内容"""
        self.content = content
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "metadata": self.metadata.to_dict(),
            "content": self.content,
            "sections": [
                {
                    "title": s.title,
                    "content": s.content,
                    "section_type": s.section_type,
                    "level": s.level,
                }
                for s in self.sections
            ],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class AnalysisResult:
    """分析结果"""
    id: str
    paper_id: str
    prompt_name: str
    content: str
    status: AnalysisStatus = AnalysisStatus.COMPLETED
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    structured_data: Optional[Dict[str, Any]] = None
    tokens_used: Optional[int] = None
    model_name: Optional[str] = None
    cost: Optional[float] = None

    @classmethod
    def create(
        cls,
        paper_id: str,
        prompt_name: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "AnalysisResult":
        """创建分析结果"""
        result_id = hashlib.md5(f"{paper_id}:{prompt_name}:{datetime.now()}".encode()).hexdigest()[:16]
        return cls(
            id=result_id,
            paper_id=paper_id,
            prompt_name=prompt_name,
            content=content,
            metadata=metadata or {},
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "paper_id": self.paper_id,
            "prompt_name": self.prompt_name,
            "content": self.content,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
            "structured_data": self.structured_data,
            "tokens_used": self.tokens_used,
            "model_name": self.model_name,
            "cost": self.cost,
        }


@dataclass
class AnalysisTask:
    """分析任务 - 应用编排层使用"""
    id: str
    paper_id: str
    prompt_name: str
    status: AnalysisStatus = AnalysisStatus.PENDING
    result: Optional[AnalysisResult] = None
    source: str = ""  # 输入来源 (本地路径或 URL)
    output_path: str = ""  # 输出路径
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @property
    def duration(self) -> float:
        """任务总耗时 (秒)"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return 0.0

    @classmethod
    def create(cls, paper_id: str, prompt_name: str) -> "AnalysisTask":
        """创建分析任务"""
        task_id = hashlib.md5(f"{paper_id}:{prompt_name}:{datetime.now()}".encode()).hexdigest()[:16]
        return cls(
            id=task_id,
            paper_id=paper_id,
            prompt_name=prompt_name,
        )

    def start(self):
        """开始任务"""
        self.status = AnalysisStatus.ANALYZING
        self.started_at = datetime.now()

    def complete(self, result: AnalysisResult):
        """完成任务"""
        self.status = AnalysisStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.now()

    def fail(self, error: str):
        """任务失败"""
        self.status = AnalysisStatus.FAILED
        self.error_message = error
        self.completed_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "paper_id": self.paper_id,
            "prompt_name": self.prompt_name,
            "status": self.status.value,
            "result": self.result.to_dict() if self.result else None,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


@dataclass
class BatchTask:
    """批量分析任务"""
    id: str
    task_name: str
    paper_ids: List[str]
    prompt_name: str
    status: AnalysisStatus = AnalysisStatus.PENDING
    results: List[AnalysisResult] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    total_count: int = 0
    success_count: int = 0
    failed_count: int = 0

    @classmethod
    def create(cls, paper_ids: List[str], prompt_name: str, task_name: str = "批量分析") -> "BatchTask":
        """创建批量任务"""
        task_id = hashlib.md5(f"{task_name}:{datetime.now()}".encode()).hexdigest()[:16]
        return cls(
            id=task_id,
            task_name=task_name,
            paper_ids=paper_ids,
            prompt_name=prompt_name,
            total_count=len(paper_ids),
        )

    def add_result(self, result: AnalysisResult, success: bool = True):
        """添加结果"""
        self.results.append(result)
        if success:
            self.success_count += 1
        else:
            self.failed_count += 1

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "task_name": self.task_name,
            "paper_ids": self.paper_ids,
            "prompt_name": self.prompt_name,
            "status": self.status.value,
            "results": [r.to_dict() for r in self.results],
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_count": self.total_count,
            "success_count": self.success_count,
            "failed_count": self.failed_count,
        }


@dataclass
class ZoteroTag:
    """Zotero 标签"""
    name: str
    color: Optional[str] = None
    tag_type: str = "manual"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ZoteroTag":
        return cls(
            name=data.get("name") or data.get("tag", ""),
            color=data.get("color"),
            tag_type=data.get("tag_type") or data.get("type", "manual"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "color": self.color,
            "tag_type": self.tag_type,
        }


@dataclass
class ZoteroCollection:
    """Zotero Collection 节点"""
    key: str
    name: str
    path: str = ""
    parent_key: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ZoteroCollection":
        return cls(
            key=data.get("key", ""),
            name=data.get("name", ""),
            path=data.get("path", ""),
            parent_key=data.get("parent_key") or data.get("parentCollection"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "name": self.name,
            "path": self.path,
            "parent_key": self.parent_key,
        }


@dataclass
class ZoteroAttachment:
    """Zotero 附件"""
    key: str
    title: str
    content_type: Optional[str] = None
    link_mode: Optional[str] = None
    path: Optional[str] = None
    url: Optional[str] = None
    md5: Optional[str] = None
    local_path: Optional[str] = None
    parent_item_key: Optional[str] = None
    is_primary: bool = False
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ZoteroAttachment":
        return cls(
            key=data.get("key", ""),
            title=data.get("title", ""),
            content_type=data.get("content_type") or data.get("contentType"),
            link_mode=data.get("link_mode") or data.get("linkMode"),
            path=data.get("path"),
            url=data.get("url"),
            md5=data.get("md5"),
            local_path=data.get("local_path"),
            parent_item_key=data.get("parent_item_key") or data.get("parentItem"),
            is_primary=data.get("is_primary", False),
            extra=data.get("extra", {}),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "title": self.title,
            "content_type": self.content_type,
            "link_mode": self.link_mode,
            "path": self.path,
            "url": self.url,
            "md5": self.md5,
            "local_path": self.local_path,
            "parent_item_key": self.parent_item_key,
            "is_primary": self.is_primary,
            "extra": self.extra,
        }


@dataclass
class ZoteroItemLink:
    """SmartPaper 与 Zotero 条目的绑定信息"""
    item_key: str
    library_id: str
    library_type: str = "user"
    version: Optional[int] = None
    parent_item_key: Optional[str] = None
    uri: Optional[str] = None
    web_url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ZoteroItemLink":
        return cls(
            item_key=data.get("item_key") or data.get("itemKey", ""),
            library_id=str(data.get("library_id") or data.get("libraryID") or ""),
            library_type=data.get("library_type") or data.get("libraryType", "user"),
            version=data.get("version"),
            parent_item_key=data.get("parent_item_key") or data.get("parentItem"),
            uri=data.get("uri"),
            web_url=data.get("web_url"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_key": self.item_key,
            "library_id": self.library_id,
            "library_type": self.library_type,
            "version": self.version,
            "parent_item_key": self.parent_item_key,
            "uri": self.uri,
            "web_url": self.web_url,
        }


@dataclass
class SyncState:
    """外部集成同步状态"""
    provider: str = "zotero"
    status: SyncStatus = SyncStatus.PENDING
    direction: SyncDirection = SyncDirection.IMPORT_ONLY
    remote_version: Optional[int] = None
    last_synced_version: Optional[int] = None
    dedupe_fingerprint: Optional[str] = None
    last_error: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SyncState":
        return cls(
            provider=data.get("provider", "zotero"),
            status=SyncStatus(data.get("status", SyncStatus.PENDING.value)),
            direction=SyncDirection(data.get("direction", SyncDirection.IMPORT_ONLY.value)),
            remote_version=data.get("remote_version"),
            last_synced_version=data.get("last_synced_version"),
            dedupe_fingerprint=data.get("dedupe_fingerprint"),
            last_error=data.get("last_error"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "status": self.status.value,
            "direction": self.direction.value,
            "remote_version": self.remote_version,
            "last_synced_version": self.last_synced_version,
            "dedupe_fingerprint": self.dedupe_fingerprint,
            "last_error": self.last_error,
        }


@dataclass
class LibraryPaperRecord:
    """文献库中的论文记录，承载 SmartPaper 与 Zotero 的映射结果"""
    paper_id: str
    title: str
    metadata: PaperMetadata
    zotero_link: ZoteroItemLink
    tags: List[ZoteroTag] = field(default_factory=list)
    collections: List[ZoteroCollection] = field(default_factory=list)
    attachments: List[ZoteroAttachment] = field(default_factory=list)
    dedupe_keys: Dict[str, str] = field(default_factory=dict)
    analysis_refs: List[str] = field(default_factory=list)
    sync_state: SyncState = field(default_factory=SyncState)
    raw_item: Dict[str, Any] = field(default_factory=dict)

    @property
    def primary_attachment(self) -> Optional[ZoteroAttachment]:
        for attachment in self.attachments:
            if attachment.is_primary:
                return attachment
        return self.attachments[0] if self.attachments else None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "metadata": self.metadata.to_dict(),
            "zotero_link": self.zotero_link.to_dict(),
            "tags": [tag.to_dict() for tag in self.tags],
            "collections": [collection.to_dict() for collection in self.collections],
            "attachments": [attachment.to_dict() for attachment in self.attachments],
            "dedupe_keys": self.dedupe_keys,
            "analysis_refs": self.analysis_refs,
            "sync_state": self.sync_state.to_dict(),
            "raw_item": self.raw_item,
        }
