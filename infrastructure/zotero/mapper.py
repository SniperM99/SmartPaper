"""Zotero -> SmartPaper 映射器"""

from __future__ import annotations

import hashlib
import re
from typing import Any, Dict, List, Optional

from domain.models import (
    LibraryPaperRecord,
    PaperMetadata,
    SyncDirection,
    SyncState,
    SyncStatus,
    ZoteroAttachment,
    ZoteroCollection,
    ZoteroItemLink,
    ZoteroTag,
)


class ZoteroItemMapper:
    """将 Zotero 条目映射到 SmartPaper 统一文献记录。"""

    def map_item(
        self,
        item: Dict[str, Any],
        collections_index: Optional[Dict[str, Dict[str, Any]]] = None,
        child_items: Optional[List[Dict[str, Any]]] = None,
        library_id: str = "",
        library_type: str = "user",
    ) -> LibraryPaperRecord:
        raw = item
        item_data = item.get("data", item)
        child_items = child_items or item.get("children", [])
        collections_index = collections_index or {}

        tags = self._map_tags(item_data.get("tags", []))
        collections = self._map_collections(item_data.get("collections", []), collections_index)
        attachments = self._map_attachments(child_items, parent_item_key=item_data.get("key"))
        dedupe_keys = self._build_dedupe_keys(item_data, attachments)
        fingerprint = self._build_fingerprint(dedupe_keys)
        primary_attachment = next((a for a in attachments if a.is_primary), None)

        metadata = PaperMetadata(
            title=item_data.get("title", ""),
            authors=self._map_authors(item_data.get("creators", [])),
            abstract=item_data.get("abstractNote"),
            journal=(
                item_data.get("publicationTitle")
                or item_data.get("proceedingsTitle")
                or item_data.get("forum")
            ),
            year=self._extract_year(item_data.get("date")),
            doi=item_data.get("DOI"),
            url=item_data.get("url"),
            file_path=primary_attachment.local_path if primary_attachment else None,
            file_hash=primary_attachment.md5 if primary_attachment else None,
            keywords=[tag.name for tag in tags],
            extra={
                "source_type": "zotero",
                "item_type": item_data.get("itemType"),
                "citation_key": item_data.get("citationKey"),
                "zotero_item_key": item_data.get("key"),
                "collections": [collection.path or collection.name for collection in collections],
                "tags": [tag.name for tag in tags],
            },
        )

        zotero_link = ZoteroItemLink(
            item_key=item_data.get("key", ""),
            library_id=str(item_data.get("libraryID", library_id or "")),
            library_type=item_data.get("libraryType", library_type),
            version=item_data.get("version"),
            uri=item_data.get("uri"),
            web_url=item_data.get("url"),
        )

        return LibraryPaperRecord(
            paper_id=fingerprint[:16],
            title=metadata.title,
            metadata=metadata,
            zotero_link=zotero_link,
            tags=tags,
            collections=collections,
            attachments=attachments,
            dedupe_keys=dedupe_keys,
            sync_state=SyncState(
                provider="zotero",
                status=SyncStatus.PENDING,
                direction=SyncDirection.IMPORT_ONLY,
                remote_version=item_data.get("version"),
                dedupe_fingerprint=fingerprint,
            ),
            raw_item=raw,
        )

    def _map_authors(self, creators: List[Dict[str, Any]]) -> List[str]:
        authors = []
        for creator in creators:
            first = creator.get("firstName", "").strip()
            last = creator.get("lastName", "").strip()
            name = creator.get("name", "").strip()
            full_name = name or " ".join(part for part in [first, last] if part)
            if full_name:
                authors.append(full_name)
        return authors

    def _map_tags(self, tags: List[Dict[str, Any]]) -> List[ZoteroTag]:
        mapped = []
        for tag in tags:
            tag_name = (tag.get("tag") or "").strip()
            if not tag_name:
                continue
            mapped.append(
                ZoteroTag(
                    name=tag_name,
                    color=tag.get("color"),
                    tag_type="automatic" if tag.get("type") == 1 else "manual",
                )
            )
        return mapped

    def _map_collections(
        self,
        collection_keys: List[str],
        collections_index: Dict[str, Dict[str, Any]],
    ) -> List[ZoteroCollection]:
        mapped = []
        for key in collection_keys:
            collection_data = collections_index.get(key, {})
            mapped.append(
                ZoteroCollection(
                    key=key,
                    name=collection_data.get("name", key),
                    path=self._build_collection_path(key, collections_index),
                    parent_key=collection_data.get("parentCollection"),
                )
            )
        return mapped

    def _build_collection_path(
        self,
        key: str,
        collections_index: Dict[str, Dict[str, Any]],
    ) -> str:
        parts: List[str] = []
        visited = set()
        current_key: Optional[str] = key
        while current_key and current_key not in visited:
            visited.add(current_key)
            collection = collections_index.get(current_key, {})
            parts.append(collection.get("name", current_key))
            current_key = collection.get("parentCollection")
        return " / ".join(reversed(parts))

    def _map_attachments(
        self,
        child_items: List[Dict[str, Any]],
        parent_item_key: Optional[str] = None,
    ) -> List[ZoteroAttachment]:
        attachments: List[ZoteroAttachment] = []
        for child in child_items:
            child_data = child.get("data", child)
            if child_data.get("itemType") != "attachment":
                continue
            attachments.append(
                ZoteroAttachment(
                    key=child_data.get("key", ""),
                    title=child_data.get("title") or child_data.get("filename") or "Attachment",
                    content_type=child_data.get("contentType"),
                    link_mode=child_data.get("linkMode"),
                    path=child_data.get("path"),
                    url=child_data.get("url"),
                    md5=child_data.get("md5"),
                    local_path=self._normalize_attachment_path(child_data.get("path")),
                    parent_item_key=child_data.get("parentItem") or parent_item_key,
                    is_primary=(child_data.get("contentType") == "application/pdf"),
                    extra={"filename": child_data.get("filename")},
                )
            )

        if attachments and not any(attachment.is_primary for attachment in attachments):
            attachments[0].is_primary = True
        return attachments

    def _normalize_attachment_path(self, path: Optional[str]) -> Optional[str]:
        if not path:
            return None
        return re.sub(r"^[A-Za-z]+:", "", path)

    def _extract_year(self, raw_date: Optional[str]) -> Optional[int]:
        if not raw_date:
            return None
        match = re.search(r"(19|20)\d{2}", raw_date)
        return int(match.group(0)) if match else None

    def _normalize_title(self, title: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", title.lower())

    def _build_dedupe_keys(
        self,
        item_data: Dict[str, Any],
        attachments: List[ZoteroAttachment],
    ) -> Dict[str, str]:
        creators = item_data.get("creators", [])
        first_author = ""
        if creators:
            first_author = creators[0].get("lastName") or creators[0].get("name") or ""

        primary_attachment = next((attachment for attachment in attachments if attachment.is_primary), None)
        dedupe_keys = {
            "zotero_item_key": item_data.get("key", ""),
            "doi": (item_data.get("DOI") or "").strip().lower(),
            "citation_key": (item_data.get("citationKey") or "").strip(),
            "normalized_title": self._normalize_title(item_data.get("title", "")),
            "title_year_author": "|".join(
                [
                    self._normalize_title(item_data.get("title", "")),
                    str(self._extract_year(item_data.get("date")) or ""),
                    str(first_author).strip().lower(),
                ]
            ),
        }
        if primary_attachment and primary_attachment.md5:
            dedupe_keys["attachment_md5"] = primary_attachment.md5.lower()
        return {key: value for key, value in dedupe_keys.items() if value}

    def _build_fingerprint(self, dedupe_keys: Dict[str, str]) -> str:
        strongest_keys = [
            dedupe_keys.get("doi"),
            dedupe_keys.get("attachment_md5"),
            dedupe_keys.get("title_year_author"),
            dedupe_keys.get("zotero_item_key"),
        ]
        seed = "||".join(value for value in strongest_keys if value)
        return hashlib.sha1(seed.encode("utf-8")).hexdigest()
