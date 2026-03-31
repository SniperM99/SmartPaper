from domain.research_map_query import (
    PaginationSchema,
    ResearchMapExportRequest,
    ResearchMapQueryRequest,
    ResearchMapQueryResponse,
    ResearchMapQueryServiceDraft,
    ResearchMapQueryFilters,
    ResearchMapQueryScope,
    ResearchMapListItem,
    PageInfoSchema,
    SortSchema,
)


def test_research_map_query_request_defaults_are_stable():
    request = ResearchMapQueryRequest()

    assert request.view == "graph"
    assert request.scope.source == "ready_cards"
    assert request.pagination.page == 1
    assert request.pagination.page_size == 20
    assert request.sort.sort_by == "label"
    assert request.sort.sort_order == "asc"
    assert request.filters.include_isolated_nodes is False


def test_research_map_query_request_supports_filter_pagination_and_sort():
    request = ResearchMapQueryRequest(
        scope=ResearchMapQueryScope(map_id="rm:test", paper_ids=["p1", "p2"], source="mixed"),
        view="gaps",
        filters=ResearchMapQueryFilters(
            years=["2024", "unknown"],
            gap_types=["explicit_gap"],
            priorities=["high"],
            min_mentions=1,
        ),
        pagination=PaginationSchema(page=2, page_size=50),
        sort=SortSchema(sort_by="priority", sort_order="asc"),
    )

    assert request.scope.map_id == "rm:test"
    assert request.scope.paper_ids == ["p1", "p2"]
    assert request.view == "gaps"
    assert request.filters.years == ["2024", "unknown"]
    assert request.pagination.page == 2
    assert request.pagination.page_size == 50
    assert request.sort.sort_by == "priority"


def test_research_map_query_response_can_wrap_ui_friendly_items():
    response = ResearchMapQueryResponse(
        view="entities",
        page_info=PageInfoSchema(page=1, page_size=20, total=1, returned=1, has_next=False),
        items=[
            ResearchMapListItem(
                item_type="entity",
                id="topic:physics-informed-ml",
                title="Physics-Informed ML",
                subtitle="topic · 2 papers",
                paper_ids=["p1", "p2"],
                sort_value="2",
                payload={"entity_type": "topic", "mentions": 2},
            )
        ],
        aggregations={"entity_type_counts": {"topic": 1}},
    )

    assert response.view == "entities"
    assert response.page_info.total == 1
    assert response.items[0].item_type == "entity"
    assert response.aggregations["entity_type_counts"]["topic"] == 1


def test_research_map_export_request_and_service_draft_are_instantiable():
    export_request = ResearchMapExportRequest(export_format="csv", flatten=True)
    draft = ResearchMapQueryServiceDraft()

    assert export_request.export_format == "csv"
    assert export_request.flatten is True
    assert "list_entities" in draft.model_dump()
    assert "export_map" in draft.model_dump()
