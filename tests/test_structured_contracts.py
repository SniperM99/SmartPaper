from domain.schemas import StructuredAnalysisData


def test_structured_analysis_can_degrade_with_missing_fields():
    data = {
        'paper_id': 'paper-1',
        'source': {'type': 'markdown', 'path': '/tmp/paper.md'},
        'metadata': {'title': 'Untitled'},
        'document': {},
        'analysis': {},
    }

    obj = StructuredAnalysisData(**data)

    assert obj.metadata.title == 'Untitled'
    assert obj.metadata.authors == []
    assert obj.document.abstract == ''
    assert obj.analysis.summary_one_sentence == ''
    assert obj.quality_control.overall_reliability == 0.0
    assert obj.trace.model_name == ''


def test_structured_analysis_contains_downstream_contract_blocks():
    obj = StructuredAnalysisData(paper_id='paper-2')
    dumped = obj.model_dump()

    for field in ['paper_id', 'source', 'metadata', 'document', 'analysis', 'quality_control', 'trace', 'citations', 'attachments', 'import_context']:
        assert field in dumped
