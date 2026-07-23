from __future__ import annotations

from backend.app.upstream.application.radar_language_context import RadarLanguageContextFactory
from backend.app.upstream.application.search_intent_planner import SearchIntentPlanner
from backend.app.upstream.application.search_triage_service import SearchResultTriageService
from backend.app.upstream.domain.radar_language import SourceLanguageInspector


def test_language_context_uses_bounded_project_language_and_records_legacy_fallback() -> None:
    factory = RadarLanguageContextFactory()

    explicit = factory.build(
        project_context={"projectId": "project-ai", "editorialLanguage": "ru"},
        workspace={"projectProfile": {"language": "en"}},
        radar={"sourceLanguagePolicy": "editorialOnly"},
    )
    legacy = factory.build(
        project_context=None,
        workspace={"projectProfile": {"language": "en"}},
        radar={},
    )

    assert explicit.project_id == "project-ai"
    assert explicit.editorial_language == "ru"
    assert explicit.allowed_source_languages == ("ru",)
    assert explicit.fallback_reason is None
    assert legacy.editorial_language == "en"
    assert legacy.source_language_policy == "editorialAndEnglish"
    assert legacy.fallback_reason == "legacy-project-language-fallback"


def test_three_source_language_policies_change_queries_and_eligibility_without_extra_calls() -> None:
    factory = RadarLanguageContextFactory()
    planner = SearchIntentPlanner()
    plans = {}
    for policy in ("editorialOnly", "editorialAndEnglish", "any"):
        radar = {**radar_fixture(), "sourceLanguagePolicy": policy}
        context = factory.build(
            project_context={"projectId": "project-ai", "editorialLanguage": "ru"},
            workspace=workspace_fixture(),
            radar=radar,
        )
        plans[policy] = planner.build(
            radar=radar,
            handles=workspace_fixture()["sourceRegistry"]["handles"],
            budget={"maxExternalQueries": 5},
            workspace=workspace_fixture(),
            language_context=context,
        ).to_payload()

    assert [item["queryLanguage"] for item in plans["editorialOnly"]["queries"]] == ["ru"] * 5
    assert [item["queryLanguage"] for item in plans["editorialAndEnglish"]["queries"]] == [
        "ru", "en", "en", "ru", "en"
    ]
    assert [item["queryLanguage"] for item in plans["any"]["queries"]] == [
        "ru", "en", "en", "ru", "en"
    ]
    assert all(len(plan["queries"]) == 5 for plan in plans.values())
    assert plans["editorialOnly"]["languageContext"]["allowedSourceLanguages"] == ["ru"]
    assert plans["editorialAndEnglish"]["languageContext"]["allowedSourceLanguages"] == ["ru", "en"]
    assert plans["any"]["languageContext"]["allowedSourceLanguages"] == []


def test_small_query_budget_records_missing_language_without_adding_provider_calls() -> None:
    radar = {**radar_fixture(), "sourceLanguagePolicy": "editorialAndEnglish"}
    context = RadarLanguageContextFactory().build(
        project_context={"projectId": "project-ai", "editorialLanguage": "ru"},
        workspace=workspace_fixture(),
        radar=radar,
    )

    plan = SearchIntentPlanner().build(
        radar=radar,
        handles=workspace_fixture()["sourceRegistry"]["handles"],
        budget={"maxExternalQueries": 1},
        workspace=workspace_fixture(),
        language_context=context,
    ).to_payload()

    assert len(plan["queries"]) == 1
    assert plan["queries"][0]["queryLanguage"] == "ru"
    assert plan["languageCoverageGaps"] == [{"language": "en", "reason": "budget-max-external-queries"}]


def test_source_language_inspector_distinguishes_russian_english_mixed_and_unknown() -> None:
    inspector = SourceLanguageInspector()

    assert inspector.inspect("Подробный промышленный кейс с ограничениями и результатом").language == "ru"
    assert inspector.inspect("Detailed industrial case with operational constraints and measurable results").language == "en"
    assert inspector.inspect("Промышленный кейс with detailed operational results and ограничения").mixed is True
    assert inspector.inspect("AI RCA").language == "unknown"


def test_editorial_only_rejects_confident_english_but_keeps_unknown_with_warning() -> None:
    workspace = workspace_fixture()
    radar = {**radar_fixture(), "sourceLanguagePolicy": "editorialOnly"}
    context = RadarLanguageContextFactory().build(
        project_context={"projectId": "project-ai", "editorialLanguage": "ru"},
        workspace=workspace,
        radar=radar,
    )
    plan = {
        "queries": [{
            "id": "query-1", "intentId": "intent-1", "sourceHandleId": "source-open-web",
            "family": "caseExample", "evidenceType": "case", "priority": 1, "query": "case", "label": "case",
        }],
        "intents": [{"id": "intent-1", "family": "caseExample", "evidenceType": "case", "priority": 1}],
    }
    raw = [
        {
            "id": "english", "sourceHandleId": "source-open-web", "queryId": "query-1",
            "title": "Detailed industrial maintenance implementation case",
            "snippet": "Operational evidence, measurable results, limitations and production roles.",
            "url": "https://example.org/english", "provider": "recorded",
        },
        {
            "id": "unknown", "sourceHandleId": "source-open-web", "queryId": "query-1",
            "title": "AI RCA", "snippet": "v2", "url": "https://example.org/unknown", "provider": "recorded",
        },
    ]

    result = SearchResultTriageService().triage(
        raw_results=raw,
        search_plan=plan,
        workspace=workspace,
        radar=radar,
        max_reads=2,
        language_context=context,
    )
    decisions = {item.raw_result_id: item for item in result.report.read_plan.decisions}

    assert decisions["english"].reason == "source-language-not-allowed"
    assert decisions["english"].status == "rejected"
    assert decisions["unknown"].source_language_eligibility_reason == "source-language-unverified"
    assert decisions["unknown"].reason != "source-language-not-allowed"


def workspace_fixture() -> dict:
    return {
        "projectProfile": {"language": "ru", "name": "Промышленный AI"},
        "sourceRegistry": {"handles": [{
            "id": "source-open-web", "type": "openWebQuery", "title": "Открытый поиск",
            "locator": "промышленный искусственный интеллект", "status": "active",
            "capabilities": {"canSearch": True, "canReadUrl": False},
        }]},
    }


def radar_fixture() -> dict:
    return {
        "id": "radar-industrial", "title": "Промышленные AI-кейсы",
        "scope": "Искать кейсы внедрения с механизмом, результатом и ограничениями",
        "sourceHandleIds": ["source-open-web"], "rules": [],
    }
