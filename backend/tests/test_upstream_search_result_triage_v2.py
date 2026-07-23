from __future__ import annotations

from typing import Any

from backend.app.application.public_evidence_ports import PublicUrlReadResult
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.openrouter_web_search_adapter import (
    OpenRouterWebSearchCitation,
    OpenRouterWebSearchResult,
)
from backend.app.settings import BackendSettings
from backend.app.upstream.application.external_run_payloads import UpstreamRadarPayloadFactory
from backend.app.upstream.application.external_run_service import UpstreamRadarExternalRunService
from backend.app.upstream.application.search_result_normalization import SearchResultNormalizer
from backend.app.upstream.application.search_triage_service import SearchResultTriageService


def test_url_normalization_removes_only_tracking_parameters() -> None:
    normalizer = SearchResultNormalizer()

    canonical, error = normalizer.canonical_url(
        "https://www.example.com/report?utm_source=radar&id=42&ref=feed#g"
    )
    meaningful, _ = normalizer.canonical_url("https://example.com/report?id=43")

    assert error is None
    assert canonical == "https://example.com/report?id=42"
    assert meaningful == "https://example.com/report?id=43"


def test_normalization_caps_provider_fields_and_handles_long_russian_text() -> None:
    candidate = SearchResultNormalizer().normalize(
        raw_result(
            "raw-1",
            title="П" * 450,
            snippet="Подробности " * 300,
        ),
        query=query("query-1", "caseExample"),
    )

    assert len(candidate.url) <= 2048
    assert len(candidate.title) == 300
    assert 1100 <= len(candidate.snippet) <= 1200
    assert len(candidate.query) <= 1000


def test_provider_mojibake_is_suppressed_before_raw_result_persistence() -> None:
    query_payload = {
        **query("query-1", "caseExample"),
        "sourceHandleId": "source-open-web",
        "requirementIds": ["requirement-industrial-context"],
    }
    citation = OpenRouterWebSearchCitation(
        title="Industrial maintenance implementation",
        url="https://example.com/case",
        snippet="РџСЂРѕРјС‹С€Р»РµРЅРЅС‹Р№ РєРµР№СЃ СЃ РїРѕРІСЂРµР¶РґРµРЅРЅС‹Рј С‚РµРєСЃС‚РѕРј",
    )

    raw = UpstreamRadarPayloadFactory().raw_result("run-1", query_payload, citation, 0)
    result = triage([raw], plan=search_plan(query_payload), max_reads=1)

    assert raw["snippet"] == ""
    assert raw["invalidReason"] == "provider-result-text-integrity-failed"
    assert raw["textIntegrity"]["status"] == "rejected"
    assert raw["textIntegrity"]["issues"][0]["field"] == "snippet"
    assert "valueHash" in raw["textIntegrity"]["issues"][0]
    assert result.report.read_plan.decisions[0].status == "invalid"
    assert result.report.read_plan.decisions[0].reason == "provider-result-text-integrity-failed"


def test_triage_groups_tracking_and_content_duplicates_with_all_handles() -> None:
    raw = [
        raw_result(
            "raw-1",
            query_id="query-1",
            url="https://cases.example/maintenance?utm_campaign=test",
            title="Industrial maintenance implementation case",
            snippet="Detailed implementation case with operational metrics and data.",
        ),
        raw_result(
            "raw-2",
            query_id="query-2",
            url="https://cases.example/maintenance",
            title="Industrial maintenance implementation case duplicate",
            snippet="A second citation for the same implementation case.",
        ),
        raw_result(
            "raw-3",
            query_id="query-3",
            url="https://mirror.example/case",
            title="Industrial maintenance implementation case",
            snippet="Detailed implementation case with operational metrics and data.",
        ),
    ]
    plan = search_plan(
        query("query-1", "broadDiscovery"),
        query("query-2", "caseExample"),
        query("query-3", "benchmarkPaper"),
    )

    result = triage(raw, plan=plan, max_reads=2)

    groups = result.report.duplicate_groups
    assert len(groups) == 1
    assert set(groups[0].raw_result_ids) == {"raw-1", "raw-2", "raw-3"}
    assert set(groups[0].query_ids) == {"query-1", "query-2", "query-3"}
    assert set(groups[0].families) == {"broadDiscovery", "caseExample", "benchmarkPaper"}
    assert result.report.decision_counts["duplicate"] == 2
    assert result.report.decision_counts["selected"] == 1


def test_provider_result_permutation_does_not_change_read_plan() -> None:
    raw = quality_fixture()
    plan = search_plan(
        query("query-1", "broadDiscovery"),
        query("query-2", "caseExample"),
        query("query-3", "benchmarkPaper"),
    )

    forward = triage(raw, plan=plan, max_reads=2)
    reversed_result = triage(list(reversed(raw)), plan=plan, max_reads=2)

    assert selected_urls(forward) == selected_urls(reversed_result)
    assert [group.to_payload() for group in forward.report.duplicate_groups] == [
        group.to_payload() for group in reversed_result.report.duplicate_groups
    ]


def test_known_pricing_noise_does_not_displace_strong_source() -> None:
    raw = quality_fixture() + [
        raw_result(
            "raw-noise",
            url="https://vendor.example/pricing",
            title="Best industrial AI pricing - buy now",
            snippet="Vendor pricing and request a demo for the industry-leading solution.",
        )
    ]

    result = triage(raw, plan=search_plan(query("query-1", "caseExample")), max_reads=1)

    assert "https://vendor.example/pricing" not in selected_urls(result)
    noise = next(item for item in result.report.read_plan.decisions if item.raw_result_id == "raw-noise")
    assert noise.status == "rejected"
    assert noise.reason == "below-quality-floor"


def test_coverage_allocator_never_promotes_below_quality_floor() -> None:
    raw = [
        raw_result(
            "raw-case",
            query_id="query-case",
            title="Industrial implementation case with data",
            snippet="Manufacturing maintenance deployment with metrics and operational results.",
        ),
        raw_result(
            "raw-limit-noise",
            query_id="query-limit",
            url="https://vendor.example/pricing",
            title="Pricing",
            snippet="Buy now vendor pricing request a demo.",
        ),
    ]
    plan = search_plan(
        query("query-case", "caseExample"),
        query("query-limit", "limitationCritique"),
    )

    result = triage(raw, plan=plan, max_reads=2)

    assert selected_urls(result) == {"https://example.com/raw-case"}
    assert {item["family"]: item["reason"] for item in result.report.read_plan.coverage_gaps}[
        "limitationCritique"
    ] == "below-quality-floor"


def test_read_allocator_covers_overlapping_requirements_once_then_diversifies_evidence() -> None:
    case_query = {
        **query("query-case", "caseExample"),
        "requirementIds": ["requirement-context", "requirement-mechanism", "requirement-result"],
    }
    report_query = {
        **query("query-report", "benchmarkPaper"),
        "requirementIds": ["requirement-source-quality"],
    }
    raw = [
        raw_result(
            "raw-case",
            query_id="query-case",
            url="https://cases.example/maintenance",
            title="Industrial maintenance implementation case",
            snippet="Manufacturing deployment with mechanism, operational data and measured results.",
        ),
        raw_result(
            "raw-report",
            query_id="query-report",
            url="https://research.example/benchmark",
            title="Independent industrial maintenance benchmark report",
            snippet="Independent benchmark with measurements, limitations and operational evidence.",
        ),
    ]

    result = triage(raw, plan=search_plan(case_query, report_query), max_reads=2)

    selected = [item for item in result.report.read_plan.decisions if item.status == "selected"]
    assert {item.families[0] for item in selected} == {"caseExample", "benchmarkPaper"}
    assert set(result.report.read_plan.covered_requirement_ids) == {
        "requirement-context",
        "requirement-mechanism",
        "requirement-result",
        "requirement-source-quality",
    }


def test_read_allocator_rejects_unsupported_pdf_and_selects_readable_alternative() -> None:
    raw = [
        raw_result(
            "raw-pdf",
            url="https://vendor.example/case-study.pdf?utm_source=search",
            title="Industrial maintenance implementation case with metrics",
            snippet="Manufacturing maintenance deployment with data and operational results.",
        ),
        raw_result(
            "raw-html",
            url="https://cases.example/maintenance-case",
            title="Industrial maintenance implementation case",
            snippet="Manufacturing maintenance deployment with data, constraints and results.",
        ),
    ]

    result = triage(raw, plan=search_plan(query("query-1", "caseExample")), max_reads=1)

    assert selected_urls(result) == {"https://cases.example/maintenance-case"}
    pdf_decision = next(
        item for item in result.report.read_plan.decisions if item.raw_result_id == "raw-pdf"
    )
    assert pdf_decision.status == "rejected"
    assert pdf_decision.reason == "unsupported-read-format"


def test_triage_stress_keeps_one_decision_per_100_results_and_bounded_reads() -> None:
    families = ["broadDiscovery", "caseExample", "benchmarkPaper", "ossTooling", "limitationCritique"]
    queries = [query(f"query-{index}", family) for index, family in enumerate(families, start=1)]
    raw = [
        raw_result(
            f"raw-{index:03d}",
            query_id=queries[index % len(queries)]["id"],
            url=f"https://source-{index % 17}.example/report/{index}?utm_source=stress",
            title=f"Industrial maintenance implementation case {index}",
            snippet=("Operational data, metrics, constraints, lessons and reliability results. " * 30),
        )
        for index in range(100)
    ]

    result = triage(raw, plan=search_plan(*queries), max_reads=2)

    assert result.report.decision_counts["total"] == 100
    assert result.report.decision_counts["selected"] == 2
    assert len(result.selected_for_read) == 2
    assert len(result.rejected_before_read) == 98
    assert sum(result.report.decision_counts[key] for key in ("selected", "rejected", "duplicate", "invalid", "deferredByBudget")) == 100


def test_failed_url_read_is_failed_operation_and_metadata_only_material() -> None:
    result = external_service(FailingReader()).run(workspace=external_workspace(), radar_id="radar-1")
    run = result["run"]

    read_operation = next(item for item in run["operations"] if item["kind"] == "readUrl")
    material = result["foundMaterials"][0]
    outcome = run["searchTriage"]["readOutcomes"][0]
    assert read_operation["status"] == "failed"
    assert material["status"] == "metadataOnly"
    assert outcome["status"] == "failed"
    assert outcome["readable"] is False
    assert run["status"] == "partial"
    assert "no-readable-found-materials" in run["warnings"]


def test_discovery_trace_handles_resolve_without_copying_snippets() -> None:
    result = external_service(SuccessReader()).run(workspace=external_workspace(), radar_id="radar-1")
    run = result["run"]
    material = result["foundMaterials"][0]
    trace = material["discoveryTrace"]

    assert set(trace["rawResultIds"]) <= {item["id"] for item in run["rawResults"]}
    assert set(trace["queryIds"]) <= {item["id"] for item in run["searchPlan"]["queries"]}
    assert set(trace["intentIds"]) <= {item["id"] for item in run["searchPlan"]["intents"]}
    assert trace["duplicateGroupId"] in {item["id"] for item in run["searchTriage"]["duplicateGroups"]}
    assert "snippet" not in trace
    assert "rawResults" not in trace


def triage(raw: list[dict[str, Any]], *, plan: dict[str, Any], max_reads: int):
    return SearchResultTriageService().triage(
        raw_results=raw,
        search_plan=plan,
        workspace={"projectProfile": {"name": "Industrial AI workshop", "description": "Maintenance and EAM"}},
        radar={"title": "Industrial AI", "scope": "Maintenance implementation evidence", "rules": []},
        max_reads=max_reads,
    )


def selected_urls(result) -> set[str]:
    return {item["url"] for item in result.selected_for_read}


def raw_result(
    item_id: str,
    *,
    query_id: str = "query-1",
    url: str | None = None,
    title: str = "Industrial maintenance implementation case",
    snippet: str = "Operational data, metrics and reliability results.",
) -> dict[str, Any]:
    return {
        "id": item_id,
        "sourceHandleId": "source-open-web",
        "queryId": query_id,
        "title": title,
        "url": url or f"https://example.com/{item_id}",
        "snippet": snippet,
        "provider": "openrouter:web_search",
    }


def query(query_id: str, family: str) -> dict[str, Any]:
    return {
        "id": query_id,
        "intentId": f"intent-{family}",
        "sourceHandleId": "source-open-web",
        "family": family,
        "evidenceType": family,
        "priority": {
            "broadDiscovery": 1,
            "caseExample": 2,
            "benchmarkPaper": 3,
            "ossTooling": 4,
            "limitationCritique": 5,
        }.get(family, 9),
        "query": f"industrial maintenance {family} data metrics constraints",
        "label": family,
    }


def search_plan(*queries: dict[str, Any]) -> dict[str, Any]:
    return {
        "queries": list(queries),
        "intents": [
            {
                "id": item["intentId"],
                "family": item["family"],
                "evidenceType": item["evidenceType"],
                "priority": item["priority"],
            }
            for item in queries
        ],
    }


def quality_fixture() -> list[dict[str, Any]]:
    return [
        raw_result(
            "raw-broad",
            query_id="query-1",
            title="Industrial asset reliability overview",
            snippet="Maintenance data and reliability practice across manufacturing sites.",
        ),
        raw_result(
            "raw-case",
            query_id="query-2",
            title="Predictive maintenance implementation case",
            snippet="Deployment used operational data and reported 18% downtime reduction in 2025.",
        ),
        raw_result(
            "raw-paper",
            query_id="query-3",
            title="Benchmark paper for industrial maintenance",
            snippet="Research methodology, dataset, metrics and benchmark results for asset reliability.",
        ),
    ]


class SearchAdapter:
    def search(self, **_: Any) -> OpenRouterWebSearchResult:
        return OpenRouterWebSearchResult(
            content="search",
            citations=[
                OpenRouterWebSearchCitation(
                    title="Industrial maintenance implementation case",
                    url="https://case.example/maintenance?utm_source=test",
                    snippet="Operational data, metrics and reliability results.",
                ),
                OpenRouterWebSearchCitation(
                    title="Industrial maintenance implementation case duplicate",
                    url="https://case.example/maintenance",
                    snippet="Second citation for the same case.",
                ),
            ],
            raw_response={"id": "search-1", "model": "test-model", "usage": {"prompt_tokens": 120}},
        )


class SuccessReader:
    def read(self, url: str) -> PublicUrlReadResult:
        return PublicUrlReadResult(url=url, final_url=url, title="Read case", text="Detailed readable case.")


class FailingReader:
    def read(self, url: str) -> PublicUrlReadResult:
        raise TimeoutError(f"cannot read {url}")


def external_service(reader) -> UpstreamRadarExternalRunService:
    return UpstreamRadarExternalRunService(
        settings=BackendSettings(
            OPENROUTER_API_KEY="test-token",
            OPENROUTER_DEFAULT_MODEL="test-model",
            OPENROUTER_WEB_TOOLS_ENABLED=True,
            OPENROUTER_WEB_SEARCH_MODEL="test-model",
            OPENROUTER_WEB_SEARCH_MAX_RESULTS=5,
            DRAFT_RUN_EXECUTION_MODE="smoke",
        ),
        web_search_adapter=SearchAdapter(),
        url_reader=reader,
        openrouter_validator=OpenRouterConfigValidator(),
    )


def external_workspace() -> dict[str, Any]:
    return {
        "projectProfile": {"language": "en", "name": "Industrial AI"},
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
                "id": "radar-1",
                "title": "Industrial AI radar",
                "scope": "Find industrial AI implementation patterns",
                "sourceHandleIds": ["source-open-web"],
                "rules": [{"statement": "Operational proof"}],
            }
        ],
        "radarRuns": [],
    }
