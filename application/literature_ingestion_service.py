"""统一文献导入与解析服务。

将 PDF、URL、未来扩展来源以及 Zotero 附件统一为 NormalizedPaperSchema，
供上游分析与下游知识卡抽取复用。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse
import hashlib
import os
import re

import requests
from loguru import logger

from domain.schemas import (
    AttachmentSchema,
    CitationSchema,
    DocumentSchema,
    ImportContextSchema,
    MetadataSchema,
    NormalizedPaperSchema,
    SectionSchema,
    SourceSchema,
)
from infrastructure.pdf.pdf_converter import PDFConverter
from src.utils.section_splitter import SectionSplitter


class LiteratureIngestionService:
    """多源统一导入服务。"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.pdf_converter = PDFConverter(
            converter_name=self.config.get("document_converter", {}).get("converter_name", "markitdown"),
            config=self.config,
        )

    def import_source(self, source: Union[str, Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        descriptor = self._normalize_source_descriptor(source, metadata or {})
        content, extracted_meta = self._read_content(descriptor)
        section_map = SectionSplitter.split(content) if content else {}
        merged_metadata = self._merge_metadata(descriptor, extracted_meta, content, section_map)
        citations = self._extract_citations(section_map.get("references", ""))
        attachments = self._extract_attachments(descriptor)
        import_context = self._build_import_context(descriptor)
        paper_id = self._build_paper_id(descriptor, content)

        normalized = NormalizedPaperSchema(
            paper_id=paper_id,
            source=SourceSchema(**descriptor["source"]),
            metadata=MetadataSchema(**merged_metadata),
            content=content,
            section_map=section_map,
            sections=self._build_sections(section_map),
            citations=[CitationSchema(**item) for item in citations],
            attachments=[AttachmentSchema(**item) for item in attachments],
            import_context=ImportContextSchema(**import_context),
            document=DocumentSchema(
                abstract=section_map.get("abstract", "")[:4000],
                sections=list(section_map.keys()),
                references=[item.get("title") or item.get("raw_text", "")[:240] for item in citations[:20]],
            ),
        )
        return normalized.model_dump()

    def _normalize_source_descriptor(self, source: Union[str, Dict[str, Any]], metadata: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(source, dict):
            descriptor = {**source}
        else:
            descriptor = {"locator": source}

        locator = descriptor.get("locator") or descriptor.get("path") or descriptor.get("url") or ""
        locator = str(locator)
        parsed = urlparse(locator) if locator.startswith(("http://", "https://")) else None
        is_url = bool(parsed and parsed.scheme in {"http", "https"})

        source_type = descriptor.get("type")
        path = descriptor.get("path", "")
        url = descriptor.get("url", "")
        mime_type = descriptor.get("mime_type", "")

        if not source_type:
            if is_url:
                if "arxiv.org" in parsed.netloc:
                    source_type = "arxiv"
                else:
                    source_type = "url"
                url = locator
            else:
                path = locator
                suffix = Path(locator).suffix.lower()
                if suffix == ".pdf":
                    source_type = "pdf"
                    mime_type = mime_type or "application/pdf"
                elif suffix in {".md", ".markdown"}:
                    source_type = "markdown"
                    mime_type = mime_type or "text/markdown"
                elif suffix in {".txt", ".text"}:
                    source_type = "text"
                    mime_type = mime_type or "text/plain"
                else:
                    source_type = "unknown"

        if source_type == "arxiv":
            url = self._normalize_arxiv_url(url or locator)
            mime_type = mime_type or "application/pdf"
        elif source_type == "url" and (url or locator).lower().endswith(".pdf"):
            mime_type = mime_type or "application/pdf"
        elif source_type == "zotero_attachment":
            path = descriptor.get("path", path)
            url = descriptor.get("url", url)
            mime_type = mime_type or ("application/pdf" if str(path).lower().endswith(".pdf") else "")

        descriptor["source"] = {
            "type": source_type,
            "path": path,
            "url": url,
            "canonical_uri": url or path or locator,
            "mime_type": mime_type,
        }
        descriptor["provided_metadata"] = metadata or descriptor.get("metadata", {})
        return descriptor

    def _read_content(self, descriptor: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        source = descriptor["source"]
        source_type = source["type"]

        if source_type in {"pdf", "zotero_attachment"} and source["path"]:
            result = self.pdf_converter.convert_file(source["path"])
            return result.get("text_content", ""), result.get("metadata", {})

        if source_type in {"url", "arxiv", "zotero_attachment"} and source["url"]:
            if source.get("mime_type") == "application/pdf" or source["url"].lower().endswith(".pdf"):
                result = self.pdf_converter.convert_url(source["url"])
                result_meta = result.get("metadata", {})
                result_meta["url"] = source["url"]
                return result.get("text_content", ""), result_meta
            return self._read_html(source["url"])

        if source_type in {"markdown", "text", "unknown"} and source["path"]:
            file_path = Path(source["path"])
            if not file_path.exists():
                raise ValueError(f"文件不存在: {file_path}")
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            return text, {"title": file_path.stem}

        if source_type == "zotero_item":
            provided = descriptor.get("provided_metadata", {})
            abstract = provided.get("abstract") or provided.get("abstractNote") or ""
            title = provided.get("title") or descriptor.get("title") or ""
            synthetic_text = f"# {title}\n\n## Abstract\n{abstract}".strip()
            return synthetic_text, provided

        raise ValueError(f"暂不支持的输入源: {source}")

    def _read_html(self, url: str) -> tuple[str, Dict[str, Any]]:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        html = response.text
        title_match = re.search(r"<title>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
        title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else ""
        text = re.sub(r"<script.*?>.*?</script>", " ", html, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<style.*?>.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text, {"title": title, "url": url}

    def _merge_metadata(self, descriptor: Dict[str, Any], extracted: Dict[str, Any], content: str, section_map: Dict[str, str]) -> Dict[str, Any]:
        provided = descriptor.get("provided_metadata", {}) or {}
        combined = {**extracted, **provided}

        fallback_stem = Path(descriptor["source"].get("path") or descriptor["source"].get("url") or "paper").stem
        extracted_title = self._extract_title_from_content(content)
        raw_title = combined.get("title") or ""
        title = extracted_title or (raw_title if raw_title and raw_title != fallback_stem else "") or fallback_stem
        authors = combined.get("authors") or combined.get("creators") or []
        if isinstance(authors, str):
            authors = [a.strip() for a in re.split(r"[,;]\s*", authors) if a.strip()]
        affiliations = combined.get("affiliations") or []
        keywords = combined.get("keywords") or self._extract_keywords(content)
        if isinstance(keywords, str):
            keywords = [k.strip() for k in re.split(r"[,;]\s*", keywords) if k.strip()]
        year = str(combined.get("year") or self._extract_year(content) or "")
        venue = combined.get("venue") or combined.get("journal") or combined.get("publicationTitle") or ""
        doi = combined.get("doi") or self._extract_doi(content)

        return {
            "title": title,
            "authors": authors,
            "affiliations": affiliations,
            "year": year,
            "venue": venue,
            "doi": doi,
            "keywords": keywords,
        }

    def _extract_title_from_content(self, content: str) -> str:
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        for line in lines[:20]:
            if line.startswith("#"):
                return line.lstrip("#").strip()
        for line in lines[:10]:
            if 8 < len(line) < 300 and not re.match(r"^(abstract|introduction|摘要|引言)$", line, re.I):
                return line
        return ""

    def _extract_keywords(self, content: str) -> List[str]:
        match = re.search(r"keywords?\s*[:：]\s*(.+)", content, flags=re.IGNORECASE)
        if not match:
            return []
        line = match.group(1).split("\n", 1)[0]
        return [k.strip(" .;,") for k in re.split(r"[,;，；]", line) if k.strip()]

    def _extract_year(self, content: str) -> str:
        match = re.search(r"\b(19|20)\d{2}\b", content[:4000])
        return match.group(0) if match else ""

    def _extract_doi(self, content: str) -> str:
        match = re.search(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", content, flags=re.IGNORECASE)
        return match.group(0) if match else ""

    def _extract_citations(self, references_text: str) -> List[Dict[str, Any]]:
        if not references_text.strip():
            return []

        raw_lines = [line.strip() for line in references_text.splitlines() if line.strip()]
        citations: List[Dict[str, Any]] = []
        buffer = ""
        for line in raw_lines:
            if re.match(r"^(\[\d+\]|\d+\.|•|-)", line) and buffer:
                citations.append(self._parse_citation_line(buffer))
                buffer = line
            else:
                buffer = f"{buffer} {line}".strip()
        if buffer:
            citations.append(self._parse_citation_line(buffer))
        return citations[:100]

    def _parse_citation_line(self, line: str) -> Dict[str, Any]:
        year_match = re.search(r"\b(19|20)\d{2}\b", line)
        doi_match = re.search(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", line, flags=re.IGNORECASE)
        url_match = re.search(r"https?://\S+", line)
        title = ""
        quoted = re.findall(r'“([^”]+)”|"([^"]+)"', line)
        if quoted:
            title = next((a or b for a, b in quoted if a or b), "")
        if not title and year_match:
            after_year = line[year_match.end():].strip(" .:-")
            title = after_year.split(".", 1)[0].strip()
        return {
            "raw_text": line,
            "title": title,
            "authors": [],
            "year": year_match.group(0) if year_match else "",
            "venue": "",
            "doi": doi_match.group(0) if doi_match else "",
            "url": url_match.group(0) if url_match else "",
        }

    def _extract_attachments(self, descriptor: Dict[str, Any]) -> List[Dict[str, Any]]:
        attachments = descriptor.get("attachments") or []
        source = descriptor["source"]
        if source.get("path") or source.get("url"):
            attachments = [
                {
                    "name": Path(source.get("path") or source.get("url") or "attachment").name,
                    "type": "pdf" if source.get("mime_type") == "application/pdf" or str(source.get("path", "")).lower().endswith(".pdf") else "unknown",
                    "path": source.get("path", ""),
                    "url": source.get("url", ""),
                    "mime_type": source.get("mime_type", ""),
                },
                *attachments,
            ]
        normalized = []
        for item in attachments:
            if isinstance(item, str):
                normalized.append({"name": Path(item).name, "type": "unknown", "path": item, "url": "", "mime_type": ""})
            else:
                normalized.append(item)
        return normalized

    def _build_import_context(self, descriptor: Dict[str, Any]) -> Dict[str, Any]:
        source = descriptor["source"]
        provided = descriptor.get("provided_metadata", {}) or {}
        return {
            "source_id": descriptor.get("source_id") or source.get("canonical_uri", ""),
            "parent_source_id": descriptor.get("parent_source_id", ""),
            "zotero_item_key": descriptor.get("zotero_item_key") or provided.get("itemKey", ""),
            "zotero_library_id": str(descriptor.get("zotero_library_id") or provided.get("libraryID", "")),
            "collection_keys": descriptor.get("collection_keys") or provided.get("collections", []) or [],
            "tags": descriptor.get("tags") or provided.get("tags", []) or [],
            "extra": descriptor.get("extra", {}),
        }

    def _build_paper_id(self, descriptor: Dict[str, Any], content: str) -> str:
        source = descriptor["source"]
        seed = source.get("canonical_uri") or content[:1000]
        return hashlib.md5(seed.encode("utf-8", errors="ignore")).hexdigest()[:16]

    def _build_sections(self, section_map: Dict[str, str]) -> List[SectionSchema]:
        sections = []
        for key, text in section_map.items():
            sections.append(
                SectionSchema(
                    key=key,
                    heading=key,
                    content=text,
                    word_count=len(text.split()),
                )
            )
        return sections

    def _normalize_arxiv_url(self, url: str) -> str:
        match = re.search(r"arxiv\.org/(abs|pdf)/([^/?#]+)", url)
        if not match:
            return url
        paper_id = match.group(2)
        if not paper_id.endswith(".pdf"):
            paper_id = paper_id.split("v")[0] if ".pdf" not in paper_id else paper_id
        paper_id = paper_id.replace(".pdf", "")
        normalized = f"https://arxiv.org/pdf/{paper_id}.pdf"
        logger.debug(f"归一化 arXiv URL: {url} -> {normalized}")
        return normalized
