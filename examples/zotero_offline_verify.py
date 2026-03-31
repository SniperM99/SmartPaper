"""Zotero 离线复审验证脚本。

运行方式：
    python -m examples.zotero_offline_verify
"""

from __future__ import annotations

import json
from pathlib import Path

from application.zotero_integration_service import ZoteroIntegrationService
from infrastructure.zotero.mapper import ZoteroItemMapper


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def load_json(name: str):
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


def verify_basic_payload() -> None:
    service = ZoteroIntegrationService(mapper=ZoteroItemMapper())
    records = service.import_from_export(load_json("zotero_mock_payload_basic.json"))
    assert len(records) == 1, "basic payload 应只产生 1 个主记录"
    record = records[0]

    assert record.metadata.title == "Physics-Informed Biomedical Models"
    assert record.metadata.authors == ["Alice Wang"]
    assert record.metadata.doi == "10.1000/xyz123"
    assert [tag.name for tag in record.tags] == ["PINN", "Biomedical"]
    assert record.collections[0].path == "Survey / PINN"
    assert record.primary_attachment is not None
    assert record.primary_attachment.local_path == "paper.pdf"
    assert record.sync_state.remote_version == 21

    print("[basic] item/attachment/tag/collection 映射通过")
    print(
        json.dumps(
            {
                "paper_id": record.paper_id,
                "title": record.title,
                "keywords": record.metadata.keywords,
                "collection_paths": [c.path for c in record.collections],
                "primary_attachment": record.primary_attachment.to_dict(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def verify_edge_cases() -> None:
    service = ZoteroIntegrationService(mapper=ZoteroItemMapper())
    records = service.import_from_export(load_json("zotero_mock_payload_edge_cases.json"))
    assert len(records) == 3, "edge payload 应产生 3 个主记录"

    dup_a = next(record for record in records if record.zotero_link.item_key == "ITEM_DUP_A")
    dup_b = next(record for record in records if record.zotero_link.item_key == "ITEM_DUP_B")
    meta_only = next(record for record in records if record.zotero_link.item_key == "ITEM_NO_ATTACHMENT")

    assert dup_a.dedupe_keys["doi"] == dup_b.dedupe_keys["doi"] == "10.1000/dup-001"
    assert meta_only.primary_attachment is None
    orphan_collection = next(collection for collection in dup_b.collections if collection.key == "ORPHAN")
    assert orphan_collection.path == "MISSING_PARENT / Orphan Branch"

    print("[edge] 重复 DOI / 附件缺失 / collection 嵌套退化通过")
    print(
        json.dumps(
            {
                "duplicate_doi": dup_a.dedupe_keys["doi"],
                "metadata_only_has_attachment": meta_only.primary_attachment is not None,
                "orphan_collection_path": orphan_collection.path,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    verify_basic_payload()
    verify_edge_cases()
    print("[done] Zotero 离线复审证据生成完成")
