"""工作台 UI 使用的应用层 façade。"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.history_manager import HistoryManager
from src.core.profile_manager import ProfileManager


class WorkbenchService:
    """为 Streamlit 工作台提供稳定的视图数据与轻量操作。"""

    def __init__(
        self,
        history_manager: Optional[HistoryManager] = None,
        profile_manager: Optional[ProfileManager] = None,
    ) -> None:
        self.history_manager = history_manager or HistoryManager()
        self.profile_manager = profile_manager or ProfileManager()

    def list_library_entries(self) -> List[Dict[str, Any]]:
        history = self.history_manager.list_history()
        return [self._build_library_entry(item) for item in history]

    def get_profile(self) -> Dict[str, Any]:
        return self.profile_manager.get_all()

    def update_profile(self, profile: Dict[str, Any]) -> None:
        self.profile_manager.update_profile(profile)

    def create_zotero_batch_record(
        self,
        library_name: str,
        mapping_mode: str,
        files: Optional[List[Any]] = None,
        timestamp: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "timestamp": timestamp or time.strftime("%Y-%m-%d %H:%M:%S"),
            "library": library_name or "未命名库",
            "mapping_mode": mapping_mode,
            "files": [getattr(f, "name", str(f)) for f in (files or [])],
            "status": "待后端接入",
        }

    def _build_library_entry(self, history_item: Dict[str, Any]) -> Dict[str, Any]:
        cache_key = history_item["cache_key"]
        index_entry = self.history_manager.get_history_entry(cache_key) or {}
        analysis_record = self.history_manager.get_analysis(cache_key) or {}
        structured_data = analysis_record.get("structured_data") or {}
        metadata = structured_data.get("metadata") or history_item.get("metadata") or {}
        analysis = structured_data.get("analysis") or {}
        quality = structured_data.get("quality_control") or {}

        return {
            "cache_key": cache_key,
            "file_name": history_item.get("file_name", ""),
            "file_path": analysis_record.get("file_path") or history_item.get("file_path", ""),
            "original_source": history_item.get("original_source", index_entry.get("original_source", "")),
            "prompt_name": history_item.get("prompt_name", index_entry.get("prompt_name", "Unknown")),
            "timestamp": history_item.get("timestamp", 0),
            "content": analysis_record.get("content", ""),
            "structured_data": structured_data or None,
            "title": metadata.get("title") or Path(history_item.get("file_name", "")).stem,
            "year": metadata.get("year") or "未知",
            "venue": metadata.get("venue") or metadata.get("journal") or "未提取",
            "authors": metadata.get("authors", []),
            "keywords": metadata.get("keywords", []),
            "summary": analysis.get("summary_one_sentence") or "暂无摘要",
            "method_tags": analysis.get("method_tags", []),
            "dataset_tags": analysis.get("dataset_tags", []),
            "application_tags": analysis.get("application_tags", []),
            "innovation_points": analysis.get("innovation_points", []),
            "limitations": analysis.get("limitations", []),
            "reliability": quality.get("overall_reliability"),
            "audit_metrics": index_entry.get("audit_metrics", {}),
        }
