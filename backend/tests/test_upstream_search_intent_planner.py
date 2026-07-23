from typing import Any

from backend.app.upstream.application.search_intent_planner import SearchIntentPlanner


def test_search_intent_planner_builds_typed_campaign_for_three_benchmark_shapes() -> None:
    planner = SearchIntentPlanner()

    plans = [
        planner.build(radar=workspace["radars"][0], handles=workspace["sourceRegistry"]["handles"], budget=budget(), workspace=workspace).to_payload()
        for workspace in (industrial_en_workspace(), editorial_ru_workspace(), mixed_sources_workspace())
    ]

    assert all(plan["strategy"] == "deterministic-search-campaign-v3" for plan in plans)
    assert all("intents" in plan and "trace" in plan and "sourceStrategy" in plan for plan in plans)
    assert plans[0]["intents"][0]["family"] == "broadDiscovery"
    assert plans[0]["queries"][0]["family"] == "broadDiscovery"
    assert plans[1]["language"] == "ru"
    assert plans[2]["sourceStrategy"]["directReadSourceHandleIds"] == ["source-url"]


def test_search_intent_planner_language_changes_query_text_not_intent_taxonomy() -> None:
    planner = SearchIntentPlanner()

    en_plan = planner.build(
        radar=industrial_en_workspace()["radars"][0],
        handles=industrial_en_workspace()["sourceRegistry"]["handles"],
        budget=budget(max_queries=3),
        workspace=industrial_en_workspace(),
    ).to_payload()
    ru_plan = planner.build(
        radar=editorial_ru_workspace()["radars"][0],
        handles=editorial_ru_workspace()["sourceRegistry"]["handles"],
        budget=budget(max_queries=3),
        workspace=editorial_ru_workspace(),
    ).to_payload()

    assert [intent["intentType"] for intent in en_plan["intents"][:3]] == [intent["intentType"] for intent in ru_plan["intents"][:3]]
    assert "case study" in en_plan["queries"][1]["query"]
    assert ru_plan["queries"][0]["queryLanguage"] == "ru"
    assert ru_plan["queries"][1]["queryLanguage"] == "en"
    assert "case study" in ru_plan["queries"][1]["query"]


def test_search_intent_planner_records_query_budget_and_source_skips() -> None:
    workspace = mixed_sources_workspace()
    plan = SearchIntentPlanner().build(
        radar=workspace["radars"][0],
        handles=workspace["sourceRegistry"]["handles"],
        budget=budget(max_queries=1),
        workspace=workspace,
    ).to_payload()

    assert len(plan["queries"]) == 1
    assert "budget-max-external-queries" in plan["skippedIntents"]
    assert "source-read-direct-only" in plan["skippedIntents"]
    assert "source-inactive" in plan["skippedIntents"]
    assert plan["trace"]["budgetLimits"]["maxExternalQueries"] == 1
    assert plan["trace"]["ownershipBoundary"].startswith("Search uses only bounded radar requirements")


def test_search_intent_planner_does_not_assign_topic_or_fabula_ownership() -> None:
    workspace = industrial_en_workspace()
    plan = SearchIntentPlanner().build(
        radar=workspace["radars"][0],
        handles=workspace["sourceRegistry"]["handles"],
        budget=budget(max_queries=2),
        workspace=workspace,
    ).to_payload()

    payload_text = str(plan)
    assert "topicId" not in payload_text
    assert "fabulaId" not in payload_text
    assert plan["trace"]["inputSummary"]["topicCount"] == 1
    assert plan["trace"]["inputSummary"]["fabulaCount"] == 1


def test_search_intent_planner_deduplicates_repeated_query_terms() -> None:
    workspace = industrial_en_workspace()
    workspace["sourceRegistry"]["handles"][0]["locator"] = "industrial AI industrial AI"

    plan = SearchIntentPlanner().build(
        radar=workspace["radars"][0],
        handles=workspace["sourceRegistry"]["handles"],
        budget=budget(max_queries=3),
        workspace=workspace,
    ).to_payload()

    normalized_queries = [item["query"].casefold().replace(",", "") for item in plan["queries"]]
    assert all("industrial ai industrial ai" not in query_text for query_text in normalized_queries)


def budget(*, max_queries: int = 6) -> dict[str, int]:
    return {"maxExternalQueries": max_queries, "maxUrlReads": 2, "maxFoundMaterials": 2}


def industrial_en_workspace() -> dict[str, Any]:
    return {
        "projectProfile": {"language": "en", "benchmarkRole": "industrial-ai-pattern-quality"},
        "topics": [{"id": "topic-ai", "title": "Industrial AI"}],
        "fabulas": [{"id": "fabula-case", "title": "Implementation case"}],
        "publisherRules": [{"statement": "Prefer public operational proof."}],
        "sourceRegistry": {
            "handles": [
                {
                    "id": "source-open-web",
                    "type": "openWebQuery",
                    "title": "Industrial AI web",
                    "locator": "industrial AI maintenance",
                    "status": "active",
                    "capabilities": {"canSearch": True, "canReadUrl": False},
                }
            ]
        },
        "radars": [
            {
                "id": "radar-industrial",
                "title": "Industrial AI radar",
                "scope": "Find industrial AI implementation patterns",
                "sourceHandleIds": ["source-open-web"],
                "rules": [{"statement": "Predictive maintenance with operational proof"}],
            }
        ],
    }


def editorial_ru_workspace() -> dict[str, Any]:
    return {
        "projectProfile": {"language": "ru"},
        "topics": [{"id": "topic-editorial", "title": "Редакционная система"}],
        "fabulas": [{"id": "fabula-method", "title": "Метод"}],
        "sourceRegistry": {
            "handles": [
                {
                    "id": "source-ru-web",
                    "type": "openWebQuery",
                    "title": "Редакционная практика",
                    "locator": "редакционный процесс",
                    "status": "active",
                    "capabilities": {"canSearch": True, "canReadUrl": False},
                }
            ]
        },
        "radars": [
            {
                "id": "radar-editorial",
                "title": "Редакционный радар",
                "scope": "Искать свежие практики редакций",
                "sourceHandleIds": ["source-ru-web"],
                "rules": [{"statement": "Нужны кейсы и ограничения"}],
            }
        ],
    }


def mixed_sources_workspace() -> dict[str, Any]:
    return {
        "projectProfile": {"language": "en", "researchDepth": "standard"},
        "sourceRegistry": {
            "handles": [
                {
                    "id": "source-open-web",
                    "type": "openWebQuery",
                    "title": "AI web",
                    "locator": "AI products",
                    "status": "active",
                    "capabilities": {"canSearch": True, "canReadUrl": False},
                },
                {
                    "id": "source-url",
                    "type": "externalUrl",
                    "title": "Known report",
                    "locator": "https://example.com/report",
                    "status": "active",
                    "capabilities": {"canSearch": False, "canReadUrl": True},
                },
                {
                    "id": "source-paused",
                    "type": "openWebQuery",
                    "title": "Paused source",
                    "locator": "paused",
                    "status": "paused",
                    "capabilities": {"canSearch": True, "canReadUrl": False},
                },
            ]
        },
        "radars": [
            {
                "id": "radar-mixed",
                "title": "Mixed radar",
                "scope": "Find examples",
                "sourceHandleIds": ["source-open-web", "source-url", "source-paused"],
                "rules": [],
            }
        ],
    }
