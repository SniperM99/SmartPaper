from application.paper_analysis_service import PaperAnalysisService


def test_build_fallback_structured_data_produces_complete_contract():
    result = PaperAnalysisService._build_fallback_structured_data(
        paper_id='paper-x',
        original_metadata={'title': 'Fallback Title'},
        parsed_document={
            'source': {'type': 'markdown', 'path': '/tmp/paper.md'},
            'document': {'abstract': 'abstract text', 'sections': ['abstract']},
            'citations': [{'raw_text': 'ref 1'}],
            'attachments': [{'name': 'paper.md', 'type': 'unknown', 'path': '/tmp/paper.md'}],
            'import_context': {'source_id': 'src-1'},
        },
        trace_info={'model_name': 'offline'},
        quality_scores={'overall_reliability': 0.2},
        analysis_content='summary line',
    )

    assert result['paper_id'] == 'paper-x'
    assert result['metadata']['title'] == 'Fallback Title'
    assert result['document']['abstract'] == 'abstract text'
    assert result['analysis']['summary_one_sentence'] == 'summary line'
    assert result['quality_control']['overall_reliability'] == 0.2
    assert result['trace']['model_name'] == 'offline'
    assert result['citations'][0]['raw_text'] == 'ref 1'
    assert result['attachments'][0]['name'] == 'paper.md'
