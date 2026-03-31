"""Zotero 客户端抽象与离线导出加载器"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


class BaseZoteroClient(ABC):
    """Zotero 客户端抽象。

    当前先定义协议，后续可接 Web API、桌面插件桥接或本地连接器。
    """

    @abstractmethod
    def list_items(self, since_version: Optional[int] = None) -> List[Dict[str, Any]]:
        """列出条目，可用于全量导入或增量同步。"""

    @abstractmethod
    def list_collections(self) -> List[Dict[str, Any]]:
        """列出 collections 层级。"""

    @abstractmethod
    def list_children(self, item_key: str) -> List[Dict[str, Any]]:
        """列出附件、note、annotation 等子项。"""

    @abstractmethod
    def get_item_versions(self, item_keys: Optional[Iterable[str]] = None) -> Dict[str, int]:
        """获取远端版本，用于增量同步与冲突检测。"""

    @abstractmethod
    def upsert_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """预留未来回写入口：更新元数据。"""

    @abstractmethod
    def create_note(self, parent_item_key: str, note_html: str) -> Dict[str, Any]:
        """预留未来回写入口：写入 SmartPaper 分析 note。"""

    @abstractmethod
    def update_tags(self, item_key: str, tags: List[Dict[str, Any]]) -> Dict[str, Any]:
        """预留未来回写入口：更新 SmartPaper 标签。"""


class ZoteroExportLoader:
    """兼容 Zotero JSON 导出文件的轻量加载器。"""

    def load(self, file_path: str) -> Dict[str, Any]:
        payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return {"items": payload, "collections": []}
        return payload
