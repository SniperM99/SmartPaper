from pathlib import Path

from application.literature_ingestion_service import LiteratureIngestionService


def test_import_markdown_source(tmp_path: Path):
    md_file = tmp_path / 'paper.md'
    md_file.write_text(
        '# Demo Paper\n\n## Abstract\nA short abstract.\n\n## Method\nMethod details.\n\n## References\n[1] Smith. 2024. "Prior Work". https://example.com\n',
        encoding='utf-8',
    )

    service = LiteratureIngestionService(config={})
    result = service.import_source(str(md_file), metadata={'keywords': ['demo', 'test']})

    assert result['source']['type'] == 'markdown'
    assert result['metadata']['title'] == 'Demo Paper'
    assert result['document']['abstract'].startswith('A short abstract')
    assert 'method' in result['section_map']
    assert result['citations'][0]['year'] == '2024'
    assert result['attachments'][0]['path'] == str(md_file)


def test_import_zotero_item_without_attachment():
    service = LiteratureIngestionService(config={})
    result = service.import_source(
        {
            'type': 'zotero_item',
            'metadata': {
                'title': 'Zotero Imported Paper',
                'abstractNote': 'Imported from Zotero abstract.',
                'itemKey': 'ABCD1234',
                'libraryID': 42,
                'collections': ['COL1'],
                'tags': ['survey'],
                'year': '2025',
            },
        }
    )

    assert result['source']['type'] == 'zotero_item'
    assert result['metadata']['title'] == 'Zotero Imported Paper'
    assert result['import_context']['zotero_item_key'] == 'ABCD1234'
    assert result['import_context']['zotero_library_id'] == '42'
    assert result['document']['abstract'].startswith('Imported from Zotero abstract')


def test_arxiv_url_is_normalized_to_pdf():
    service = LiteratureIngestionService(config={})
    url = service._normalize_arxiv_url('https://arxiv.org/abs/2305.12002v2')
    assert url == 'https://arxiv.org/pdf/2305.12002.pdf'
