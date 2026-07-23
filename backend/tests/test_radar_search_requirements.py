from backend.app.upstream.application.search_intent_planner import SearchIntentPlanner
from backend.app.upstream.application.search_requirement_profile import RadarSearchRequirementProfileFactory


def test_filter_modes_become_search_roles_or_explicit_scoring_only_decisions() -> None:
    radar = {
        "id": "radar-industrial",
        "title": "Промышленные AI-кейсы",
        "scope": "Промышленный AI и ТОиР",
        "filters": [
            filter_rule("topic", "topics", "mustMatch"),
            filter_rule("mechanism", "mechanism", "shouldMatch"),
            filter_rule("noise", "promotionalNoise", "mustNotMatch"),
            filter_rule("tension", "productiveTension", "seekTension"),
            filter_rule("author", "author", "shouldMatch"),
        ],
    }

    profile = RadarSearchRequirementProfileFactory().build(radar)

    assert {item.filter_id: item.role for item in profile.requirements} == {
        "mechanism": "optional",
        "noise": "exclusion",
        "tension": "tension",
        "topic": "required",
    }
    assert [item.filter_id for item in profile.not_search_applicable] == ["author"]
    assert profile.not_search_applicable[0].reason == "project-setting-is-scoring-only"


def test_standard_industrial_plan_allocates_case_benchmark_and_critique_first() -> None:
    radar = industrial_radar()
    plan = SearchIntentPlanner().build(
        radar=radar,
        handles=[search_handle()],
        budget={"maxExternalQueries": 3, "maxUrlReads": 2, "maxFoundMaterials": 2},
        workspace={"projectProfile": {"language": "en", "researchDepth": "standard"}},
    ).to_payload()

    assert [item["family"] for item in plan["queries"]] == [
        "caseExample",
        "benchmarkPaper",
        "limitationCritique",
    ]
    assert all(item["requirementIds"] for item in plan["queries"])
    assert plan["uncoveredRequiredSearchRequirements"] == []
    assert len({" ".join(item["query"].casefold().split()) for item in plan["queries"]}) == 3


def test_zero_and_small_query_caps_report_uncovered_required_requirements() -> None:
    radar = industrial_radar()
    zero = SearchIntentPlanner().build(
        radar=radar,
        handles=[search_handle()],
        budget={"maxExternalQueries": 0},
        workspace={"projectProfile": {"language": "en"}},
    ).to_payload()
    one = SearchIntentPlanner().build(
        radar=radar,
        handles=[search_handle()],
        budget={"maxExternalQueries": 1},
        workspace={"projectProfile": {"language": "en"}},
    ).to_payload()

    assert zero["queries"] == []
    assert {item["reason"] for item in zero["uncoveredRequiredSearchRequirements"]} == {"external-query-budget-zero"}
    assert len(one["queries"]) == 1
    assert one["uncoveredRequiredSearchRequirements"]


def test_large_project_context_does_not_expand_search_provider_input() -> None:
    radar = industrial_radar()
    base = {"projectProfile": {"language": "en"}}
    stress = {
        **base,
        "topics": [{"id": f"topic-{index}", "title": "x" * 1000} for index in range(100)],
        "publisherRules": [{"id": f"rule-{index}", "statement": "y" * 1000} for index in range(100)],
        "publications": [{"id": f"post-{index}", "text": "z" * 10000} for index in range(100)],
    }
    planner = SearchIntentPlanner()
    regular = planner.build(radar=radar, handles=[search_handle()], budget={"maxExternalQueries": 3}, workspace=base).to_payload()
    stressed = planner.build(radar=radar, handles=[search_handle()], budget={"maxExternalQueries": 3}, workspace=stress).to_payload()

    assert [item["query"] for item in stressed["queries"]] == [item["query"] for item in regular["queries"]]
    assert all(len(item["query"]) <= 240 for item in stressed["queries"])
    assert "publications" in stressed["requirementProfile"]["suppressedFields"]


def industrial_radar() -> dict:
    return {
        "id": "radar-industrial",
        "title": "Industrial AI cases",
        "scope": "Industrial AI maintenance implementation",
        "filters": [
            filter_rule("context", "topics", "mustMatch"),
            filter_rule("mechanism", "mechanism", "mustMatch"),
            filter_rule("outcome", "observableOutcome", "mustMatch"),
            filter_rule("source", "sourceCredibility", "mustMatch"),
            filter_rule("action", "actionability", "shouldMatch"),
            filter_rule("novelty", "novelty", "shouldMatch"),
            filter_rule("noise", "promotionalNoise", "mustNotMatch"),
            filter_rule("tension", "productiveTension", "seekTension"),
        ],
    }


def filter_rule(item_id: str, dimension: str, mode: str) -> dict:
    return {
        "id": item_id,
        "dimension": dimension,
        "mode": mode,
        "enabled": True,
        "instruction": f"Evidence for {dimension}",
    }


def search_handle() -> dict:
    return {
        "id": "source-web",
        "type": "openWebQuery",
        "title": "Industrial web",
        "locator": "industrial AI maintenance",
        "status": "active",
        "capabilities": {"canSearch": True},
    }
