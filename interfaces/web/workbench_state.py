"""工作台纯状态函数，便于脱离 Streamlit 做轻量验证。"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence


def ensure_session_defaults(state: Dict[str, Any]) -> Dict[str, Any]:
    defaults = {
        "workspace": "overview",
        "active_paper_key": None,
        "compare_keys": [],
        "library_query": "",
        "qa_messages": [],
        "zotero_batches": [],
        "last_analysis_output": None,
    }
    result = dict(state)
    for key, value in defaults.items():
        result.setdefault(key, value)
    return result


def build_overview_metrics(entries: Sequence[Dict[str, Any]], active_paper_key: Optional[str], compare_keys: Sequence[str], zotero_batches: Sequence[Dict[str, Any]]) -> Dict[str, int]:
    return {
        "paper_count": len(entries),
        "active_paper_count": 1 if active_paper_key else 0,
        "compare_count": len(compare_keys),
        "zotero_batch_count": len(zotero_batches),
    }


def build_workflow_steps(entries: Sequence[Dict[str, Any]], active_paper_key: Optional[str], compare_keys: Sequence[str]) -> List[Dict[str, str]]:
    return [
        {"step": "1. 导入源", "status": "已完成" if entries else "待开始"},
        {"step": "2. 论文入库", "status": "已完成" if entries else "待开始"},
        {"step": "3. 主论文定位", "status": "已完成" if active_paper_key else "待选择"},
        {"step": "4. 多篇对比", "status": "已完成" if len(compare_keys) >= 2 else "待准备"},
        {"step": "5. Zotero 接入", "status": "可配置"},
    ]


def filter_library_entries(entries: Sequence[Dict[str, Any]], query: str = "", selected_year: str = "全部", selected_task: str = "全部") -> List[Dict[str, Any]]:
    filtered: List[Dict[str, Any]] = []
    query_lower = (query or "").lower().strip()
    for entry in entries:
        blob = " ".join([
            entry.get("title", ""),
            entry.get("original_source", ""),
            entry.get("summary", ""),
            " ".join(entry.get("keywords", [])),
            " ".join(entry.get("method_tags", [])),
        ]).lower()
        if query_lower and query_lower not in blob:
            continue
        if selected_year != "全部" and str(entry.get("year")) != selected_year:
            continue
        if selected_task != "全部" and entry.get("prompt_name") != selected_task:
            continue
        filtered.append(entry)
    return filtered


def compare_panel_state(compare_entries: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "is_ready": len(compare_entries) >= 2,
        "warning": None if len(compare_entries) >= 2 else "至少需要 2 篇论文才能进行对比分析。",
        "titles": [entry.get("title", "") for entry in compare_entries],
    }


def research_map_scope(entries: Sequence[Dict[str, Any]], active_entry: Optional[Dict[str, Any]], compare_entries: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if compare_entries:
        return list(compare_entries)
    if active_entry:
        return [active_entry]
    return list(entries[:10])


def create_zotero_placeholder_batch(library_name: str, mapping_mode: str, files: Optional[Sequence[str]] = None, timestamp: str = "") -> Dict[str, Any]:
    return {
        "timestamp": timestamp or "1970-01-01 00:00:00",
        "library": library_name or "未命名库",
        "mapping_mode": mapping_mode,
        "files": list(files or []),
        "status": "待后端接入",
    }
