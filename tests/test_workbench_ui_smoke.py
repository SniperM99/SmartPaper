from application.workbench_service import WorkbenchService
from interfaces.web.workbench_state import (
    build_overview_metrics,
    build_workflow_steps,
    compare_panel_state,
    create_zotero_placeholder_batch,
    ensure_session_defaults,
    filter_library_entries,
    research_map_scope,
)


class FakeHistoryManager:
    def list_history(self):
        return [
            {
                "cache_key": "paper-1",
                "file_name": "paper1.md",
                "file_path": "/tmp/paper1.md",
                "original_source": "https://example.com/p1.pdf",
                "prompt_name": "phd_analysis",
                "timestamp": 1,
                "metadata": {},
            }
        ]

    def get_history_entry(self, cache_key):
        return {
            "original_source": "https://example.com/p1.pdf",
            "prompt_name": "phd_analysis",
            "audit_metrics": {"duration": 12},
        }

    def get_analysis(self, cache_key, prompt_name=None):
        return {
            "content": "# Paper 1",
            "structured_data": {
                "metadata": {"title": "Paper 1", "year": "2024", "venue": "ICLR", "authors": ["A"]},
                "analysis": {
                    "summary_one_sentence": "summary",
                    "method_tags": ["PIML"],
                    "dataset_tags": ["Dataset-A"],
                    "application_tags": ["Manufacturing"],
                    "innovation_points": ["point"],
                    "limitations": ["limit"],
                },
                "quality_control": {"overall_reliability": 0.88},
            },
            "file_path": "/tmp/paper1.md",
        }


class FakeProfileManager:
    def __init__(self):
        self.profile = {"user_context": {"role": "PhD Student"}}

    def get_all(self):
        return self.profile

    def update_profile(self, profile):
        self.profile = profile


def test_workbench_state_defaults_and_metrics():
    state = ensure_session_defaults({"session_id": "abc"})
    assert state["workspace"] == "overview"
    metrics = build_overview_metrics([], None, [], [])
    assert metrics == {
        "paper_count": 0,
        "active_paper_count": 0,
        "compare_count": 0,
        "zotero_batch_count": 0,
    }
    steps = build_workflow_steps([], None, [])
    assert steps[0]["status"] == "待开始"
    assert steps[2]["status"] == "待选择"


def test_compare_and_scope_state_validation():
    not_ready = compare_panel_state([{"title": "Only One"}])
    assert not not_ready["is_ready"]
    assert "至少需要 2 篇" in not_ready["warning"]

    ready = compare_panel_state([{"title": "A"}, {"title": "B"}])
    assert ready["is_ready"]
    assert ready["titles"] == ["A", "B"]

    entries = [{"title": "fallback-1"}, {"title": "fallback-2"}]
    assert research_map_scope(entries, {"title": "active"}, []) == [{"title": "active"}]
    assert research_map_scope(entries, None, [{"title": "compare"}]) == [{"title": "compare"}]


def test_filter_and_zotero_placeholder_state():
    entries = [
        {"title": "Paper A", "original_source": "src-a", "summary": "summary", "keywords": ["ml"], "method_tags": ["graph"], "year": "2024", "prompt_name": "phd_analysis"},
        {"title": "Paper B", "original_source": "src-b", "summary": "other", "keywords": ["vision"], "method_tags": ["cnn"], "year": "2023", "prompt_name": "summarization"},
    ]
    filtered = filter_library_entries(entries, query="graph", selected_year="2024", selected_task="phd_analysis")
    assert [item["title"] for item in filtered] == ["Paper A"]

    batch = create_zotero_placeholder_batch("My Library", "条目 + 附件", ["a.json"], timestamp="2026-03-31 10:00:00")
    assert batch["status"] == "待后端接入"
    assert batch["files"] == ["a.json"]


def test_workbench_service_builds_stable_entry_viewmodel():
    service = WorkbenchService(history_manager=FakeHistoryManager(), profile_manager=FakeProfileManager())
    entries = service.list_library_entries()
    assert len(entries) == 1
    entry = entries[0]
    assert entry["title"] == "Paper 1"
    assert entry["summary"] == "summary"
    assert entry["method_tags"] == ["PIML"]
    assert entry["audit_metrics"] == {"duration": 12}
