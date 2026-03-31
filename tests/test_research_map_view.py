import json
from pathlib import Path

from domain.research_map_view import ResearchMapGraphViewSchema, GraphNodeViewSchema, GraphEdgeViewSchema


BASE_DIR = Path(__file__).resolve().parents[1]


def test_graph_view_schema_is_stable_and_instantiable():
    view = ResearchMapGraphViewSchema(
        map_id="rm:test",
        state="ready",
        nodes=[
            GraphNodeViewSchema(
                id="paper:p1",
                kind="paper",
                label="Paper 1",
                paper_ids=["p1"],
                tags=["tag-a"],
                collections=["Col/A"],
            )
        ],
        edges=[
            GraphEdgeViewSchema(
                id="edge:1",
                kind="uses_method",
                source="paper:p1",
                target="method:m1",
                paper_ids=["p1"],
            )
        ],
        stats={"paper_count": 1},
    )

    assert view.state == "ready"
    assert view.nodes[0].kind == "paper"
    assert view.nodes[0].paper_ids == ["p1"]
    assert view.edges[0].kind == "uses_method"


def test_graph_view_fields_keep_stable_defaults_for_ui_empty_or_degraded_states():
    view = ResearchMapGraphViewSchema()

    assert view.state == "ready"
    assert view.nodes == []
    assert view.edges == []
    assert view.empty_state.state == "ready"
    assert view.empty_state.suggestions == []


def test_graph_view_example_json_is_loadable_and_contains_mapping_fields():
    with open(BASE_DIR / "examples" / "research_map_graph_view_minimal.json", "r", encoding="utf-8") as f:
        payload = json.load(f)

    view = ResearchMapGraphViewSchema(**payload)

    assert view.map_id == "rm:demo-ui-001"
    assert view.nodes[0].paper_ids == ["paper-1"]
    assert view.nodes[0].tags
    assert view.nodes[0].collections
    assert view.nodes[0].analysis_refs[0].ref_id == "cache:paper-1"
    assert view.edges[0].paper_ids == ["paper-1"]
