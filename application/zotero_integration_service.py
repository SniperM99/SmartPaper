"""Zotero 集成应用服务"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from domain.models import LibraryPaperRecord, SyncDirection
from infrastructure.zotero.client import BaseZoteroClient
from infrastructure.zotero.mapper import ZoteroItemMapper


class ZoteroIntegrationService:
    """编排 Zotero 导入、映射、增量同步预留与分析回写载荷。"""

    def __init__(
        self,
        client: Optional[BaseZoteroClient] = None,
        mapper: Optional[ZoteroItemMapper] = None,
    ):
        self.client = client
        self.mapper = mapper or ZoteroItemMapper()

    def import_from_export(self, payload: Dict[str, Any]) -> List[LibraryPaperRecord]:
        items = payload.get("items", payload if isinstance(payload, list) else [])
        collections_index = self._build_collections_index(payload.get("collections", []))
        return self._map_payload_items(items, collections_index)

    def import_from_client(self, since_version: Optional[int] = None) -> List[LibraryPaperRecord]:
        if not self.client:
            raise ValueError("Zotero client 未配置，无法执行在线导入")
        items = self.client.list_items(since_version=since_version)
        collections_index = self._build_collections_index(self.client.list_collections())
        return self._map_payload_items(items, collections_index)

    def prepare_incremental_sync(self, records: List[LibraryPaperRecord]) -> Dict[str, Any]:
        if not records:
            return {"mode": "incremental", "cursor": None, "item_keys": [], "max_remote_version": None}
        max_version = max((record.sync_state.remote_version or 0) for record in records)
        return {
            "mode": "incremental",
            "cursor": max_version,
            "item_keys": [record.zotero_link.item_key for record in records],
            "max_remote_version": max_version,
        }

    def attach_analysis_reference(self, record: LibraryPaperRecord, analysis_ref: str) -> LibraryPaperRecord:
        if analysis_ref not in record.analysis_refs:
            record.analysis_refs.append(analysis_ref)
        return record

    def prepare_writeback_payload(
        self,
        record: LibraryPaperRecord,
        analysis_summary: str,
        analysis_tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        analysis_tags = analysis_tags or []
        return {
            "provider": "zotero",
            "direction": SyncDirection.EXPORT_ANALYSIS.value,
            "target": {
                "library_id": record.zotero_link.library_id,
                "library_type": record.zotero_link.library_type,
                "item_key": record.zotero_link.item_key,
                "version": record.zotero_link.version,
            },
            "note": {
                "title": f"SmartPaper Analysis - {record.title}",
                "content_markdown": analysis_summary,
            },
            "tags_to_upsert": [{"tag": tag} for tag in analysis_tags],
            "analysis_refs": list(record.analysis_refs),
        }

    def _map_payload_items(
        self,
        items: List[Dict[str, Any]],
        collections_index: Dict[str, Dict[str, Any]],
    ) -> List[LibraryPaperRecord]:
        records: List[LibraryPaperRecord] = []
        child_index: Dict[str, List[Dict[str, Any]]] = {}

        for item in items:
            item_data = item.get("data", item)
            parent_key = item_data.get("parentItem")
            if item_data.get("itemType") == "attachment" and parent_key:
                child_index.setdefault(parent_key, []).append(item)

        for item in items:
            item_data = item.get("data", item)
            if item_data.get("itemType") in {"attachment", "note", "annotation"}:
                continue
            item_key = item_data.get("key", "")
            records.append(
                self.mapper.map_item(
                    item,
                    collections_index=collections_index,
                    child_items=item.get("children") or child_index.get(item_key, []),
                )
            )
        return records

    def _build_collections_index(self, collections: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        index: Dict[str, Dict[str, Any]] = {}
        for collection in collections:
            data = collection.get("data", collection)
            key = data.get("key")
            if key:
                index[key] = data
        return index
