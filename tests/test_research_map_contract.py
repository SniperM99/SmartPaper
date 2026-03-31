import json
from pathlib import Path

from application.research_map_service import ResearchMapService


BASE_DIR = Path(__file__).resolve().parents[1]


def load_example(name: str):
    with open(BASE_DIR / "examples" / name, "r", encoding="utf-8") as f:
        return json.load(f)


def test_research_map_contract_examples_can_build_stable_structure():
    service = ResearchMapService()
    cards = load_example("research_map_minimal_input.json")

    result = service.build_from_cards(cards)

    assert set(result.keys()) == {"overview", "entities", "relations", "timeline", "clusters", "gaps"}
    assert result["overview"]["paper_count"] == 3
    assert isinstance(result["entities"], list)
    assert isinstance(result["relations"], list)
    assert isinstance(result["timeline"], list)
    assert isinstance(result["gaps"], list)
    assert {item["year"] for item in result["timeline"]} == {"2023", "2025", "unknown"}


def test_research_map_contract_degrades_when_year_tags_or_metrics_are_missing():
    service = ResearchMapService()
    cards = [
        {
            "paper_id": "degraded-paper",
            "metadata": {"title": "Minimal Card", "year": None, "venue": "", "keywords": []},
            "analysis": {
                "summary_one_sentence": "Minimal summary",
                "research_problem": "Minimal problem",
                "topic_tags": [],
                "method_tags": [],
                "dataset_tags": [],
                "application_tags": [],
                "limitations": [],
                "future_work": [],
                "method": {"overview": "Fallback method overview"},
                "experiments": {"datasets": [], "metrics": []},
            },
        }
    ]

    result = service.build_from_cards(cards)

    assert result["overview"]["paper_count"] == 1
    assert result["timeline"][0]["year"] == "unknown"
    assert any(entity["entity_type"] == "paper" for entity in result["entities"])
    assert any(entity["entity_type"] == "problem" for entity in result["entities"])
    assert any(entity["entity_type"] == "method" for entity in result["entities"])
    assert any(gap["gap_type"] == "missing_evaluation" for gap in result["gaps"])


def test_research_map_markdown_is_auxiliary_not_primary_contract():
    service = ResearchMapService()
    cards = load_example("research_map_minimal_input.json")

    result = service.build_from_cards(cards)
    markdown = service.render_markdown(result)

    assert "# 研究地图" in markdown
    assert "## 时间线" in markdown
    assert result["overview"]["paper_count"] == 3
