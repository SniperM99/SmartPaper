import sys

sys.path.insert(0, "/Users/m99/Documents/SmartPaper")

from application.zotero_integration_service import ZoteroIntegrationService
from infrastructure.zotero.mapper import ZoteroItemMapper


def sample_payload():
    return {
        "collections": [
            {"key": "C1", "name": "Survey"},
            {"key": "C2", "name": "PINN", "parentCollection": "C1"},
        ],
        "items": [
            {
                "key": "ITEM1",
                "version": 21,
                "libraryID": 7,
                "libraryType": "user",
                "itemType": "journalArticle",
                "title": "Physics-Informed Biomedical Models",
                "creators": [{"firstName": "Alice", "lastName": "Wang"}],
                "abstractNote": "Test abstract",
                "publicationTitle": "AI Journal",
                "date": "2025-07-01",
                "DOI": "10.1000/xyz123",
                "url": "https://example.com/paper",
                "citationKey": "wang2025pibm",
                "tags": [{"tag": "PINN"}, {"tag": "Biomedical", "type": 1}],
                "collections": ["C2"],
            },
            {
                "key": "ATT1",
                "itemType": "attachment",
                "parentItem": "ITEM1",
                "title": "Main PDF",
                "contentType": "application/pdf",
                "path": "storage:paper.pdf",
                "md5": "ABCDEF123456",
            },
        ],
    }


def test_zotero_item_mapper_maps_entry_attachment_tags_and_collections():
    service = ZoteroIntegrationService(mapper=ZoteroItemMapper())
    records = service.import_from_export(sample_payload())

    assert len(records) == 1
    record = records[0]

    assert record.metadata.title == "Physics-Informed Biomedical Models"
    assert record.metadata.authors == ["Alice Wang"]
    assert record.metadata.doi == "10.1000/xyz123"
    assert [tag.name for tag in record.tags] == ["PINN", "Biomedical"]
    assert record.collections[0].path == "Survey / PINN"
    assert record.primary_attachment is not None
    assert record.primary_attachment.key == "ATT1"
    assert record.primary_attachment.local_path == "paper.pdf"
    assert record.dedupe_keys["doi"] == "10.1000/xyz123"
    assert record.sync_state.remote_version == 21


def test_prepare_incremental_sync_and_writeback_payload():
    service = ZoteroIntegrationService(mapper=ZoteroItemMapper())
    record = service.import_from_export(sample_payload())[0]
    service.attach_analysis_reference(record, "saved_analyses/analysis_001.md")

    sync_plan = service.prepare_incremental_sync([record])
    writeback = service.prepare_writeback_payload(
        record,
        analysis_summary="# Summary",
        analysis_tags=["smartpaper:reviewed", "topic:biomedical"],
    )

    assert sync_plan["cursor"] == 21
    assert sync_plan["item_keys"] == ["ITEM1"]
    assert writeback["target"]["item_key"] == "ITEM1"
    assert writeback["direction"] == "export_analysis"
    assert writeback["analysis_refs"] == ["saved_analyses/analysis_001.md"]
    assert writeback["tags_to_upsert"][0]["tag"] == "smartpaper:reviewed"
