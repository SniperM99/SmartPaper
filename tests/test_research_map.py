import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from application.research_map_service import ResearchMapService


def make_card(paper_id, title, year, keywords, problem, method_tags, datasets, metrics, limitations=None, future_work=None):
    return {
        "paper_id": paper_id,
        "metadata": {
            "title": title,
            "year": year,
            "venue": "TestConf",
            "keywords": keywords,
        },
        "analysis": {
            "summary_one_sentence": f"{title} summary.",
            "research_problem": problem,
            "method_tags": method_tags,
            "application_tags": keywords,
            "dataset_tags": datasets,
            "method": {"overview": ""},
            "experiments": {"datasets": datasets, "metrics": metrics},
            "limitations": limitations or [],
            "future_work": future_work or [],
        },
    }


def test_build_research_map_extracts_entities_relations_and_timeline():
    service = ResearchMapService()
    cards = [
        make_card(
            "p1",
            "Physics ML Survey",
            "2023",
            ["Physics-Informed ML", "Scientific Computing"],
            "How to combine physics priors with machine learning?",
            ["PINNs", "Neural Operators"],
            [],
            [],
            limitations=["Complex geometry generalization remains underexplored."],
        ),
        make_card(
            "p2",
            "Manufacturing PIML",
            "2026",
            ["Physics-Informed ML", "Manufacturing"],
            "How to transfer PIML into manufacturing processes?",
            ["PINNs"],
            ["ShopFloorBench"],
            ["RMSE", "MAE"],
            future_work=["Need broader evaluation benchmarks for manufacturing tasks."],
        ),
    ]

    research_map = service.build_from_cards(cards)

    assert research_map["overview"]["paper_count"] == 2
    assert research_map["overview"]["topic_count"] >= 2
    assert research_map["overview"]["method_count"] >= 2
    assert any(entity["entity_type"] == "topic" and entity["label"] == "Physics-Informed ML" for entity in research_map["entities"])
    assert any(rel["relation_type"] == "uses_method" for rel in research_map["relations"])
    assert any(rel["relation_type"] == "evolves_from" for rel in research_map["relations"])
    assert [event["year"] for event in research_map["timeline"]] == ["2023", "2026"]
    assert any(gap["gap_type"] == "explicit_gap" for gap in research_map["gaps"])


def test_render_markdown_contains_overview_and_gap_section():
    service = ResearchMapService()
    research_map = service.build_from_cards([
        make_card(
            "p3",
            "Single Topic Paper",
            "2025",
            ["Robotics"],
            "How to improve control policy safety?",
            ["Safe RL"],
            [],
            [],
            limitations=["Lacks standardized metrics across robot settings."],
        )
    ])

    markdown = service.render_markdown(research_map)

    assert "# 研究地图" in markdown
    assert "## 时间线" in markdown
    assert "## 候选研究空白" in markdown
    assert "Single Topic Paper" in markdown
