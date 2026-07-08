from __future__ import annotations

import json
from copy import deepcopy

from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings
from backend.app.upstream.application.benchmark import evaluate_live_radar_run
from backend.app.upstream.application.benchmark.coverage_policy import RadarBenchmarkCoveragePolicy
from backend.app.upstream.application.benchmark.evaluation_policy import RadarBenchmarkEvaluationPolicy
from backend.app.upstream.application.benchmark.trace_policy import RadarBenchmarkTracePolicy
from backend.app.upstream.application.benchmark.recorded_adapters import (
    RecordedRadarFixture,
    RecordedRadarSearchAdapter,
    RecordedUrlReader,
)
from backend.app.upstream.application.benchmark.scenarios import (
    get_golden_radar_benchmark_scenarios,
)
from backend.app.upstream.application.external_run_service import UpstreamRadarExternalRunService


def test_live_good_run_passes_without_exact_url_matching() -> None:
    scenario = _scenario()
    run, found_materials = _recorded_run()
    _add_executed_query(run, family="ossTooling", evidence_type="ossTooling")
    _add_executed_query(run, family="limitationCritique", evidence_type="limitationCritique")
    run["rawResults"][0]["url"] = "https://different.example/live-result"
    run["selectedForRead"][0]["url"] = "https://different.example/live-result"

    report = evaluate_live_radar_run(scenario=scenario, run=run, found_materials=found_materials)

    assert report.status == "passed"
    assert report.evaluation_mode == "live"
    assert report.provider_health == "ok"
    assert report.unacceptable_noise_hits == []
    assert report.executed_coverage["queryFamilies"]["missing"] == []


def test_live_planned_but_skipped_required_family_warns_instead_of_passing() -> None:
    scenario = _scenario()
    run, found_materials = _recorded_run()

    report = evaluate_live_radar_run(scenario=scenario, run=run, found_materials=found_materials)

    assert report.status == "warning"
    assert {
        (item["kind"], item["value"], item["reason"])
        for item in report.skipped_required_coverage
    } >= {
        ("queryFamily", "limitationCritique", "budget-max-external-queries"),
        ("evidenceType", "limitationCritique", "budget-max-external-queries"),
    }
    assert "intent-family:limitationCritique" in report.missing_expectations
    assert report.planned_coverage["queryFamilies"]["missing"] == []
    assert "limitationCritique" in report.executed_coverage["queryFamilies"]["missing"]


def test_live_required_family_missing_without_budget_skip_fails() -> None:
    scenario = _scenario()
    run, found_materials = _recorded_run()
    run["searchPlan"]["skippedIntentDetails"] = [
        item
        for item in run["searchPlan"]["skippedIntentDetails"]
        if item.get("family") != "limitationCritique"
    ]

    report = evaluate_live_radar_run(scenario=scenario, run=run, found_materials=found_materials)

    assert report.status == "failed"
    assert report.skipped_required_coverage == []
    assert "intent-family:limitationCritique" in report.missing_expectations


def test_live_partial_run_warns_for_provider_degradation() -> None:
    scenario = _scenario()
    run, found_materials = _recorded_run()
    run["operations"][0]["status"] = "failed"
    run["operations"][0]["error"] = "provider-500"

    report = evaluate_live_radar_run(scenario=scenario, run=run, found_materials=found_materials)

    assert report.status == "warning"
    assert report.provider_health == "degraded"
    assert report.inconclusive_reasons == []


def test_live_noise_in_accepted_material_fails_quality() -> None:
    scenario = _scenario()
    run, found_materials = _recorded_run()
    found_materials[0]["summary"] = "Generic AI news and vendor pricing accepted as source material."

    report = evaluate_live_radar_run(scenario=scenario, run=run, found_materials=found_materials)

    assert report.status == "failed"
    assert report.unacceptable_noise_hits == [found_materials[0]["id"]]


def test_live_provider_unavailable_is_inconclusive_not_quality_failure() -> None:
    scenario = _scenario()
    run, found_materials = _recorded_run()
    run["operations"] = [
        {
            "id": "op-search",
            "kind": "openWebQuery",
            "status": "skipped",
            "skippedReason": "openrouter-not-configured",
        }
    ]
    run["rawResults"] = []
    run["selectedForRead"] = []
    run["foundMaterialIds"] = []
    found_materials.clear()

    report = evaluate_live_radar_run(scenario=scenario, run=run, found_materials=found_materials)

    assert report.status == "inconclusive"
    assert report.provider_health == "unavailable"
    assert "openrouter-not-configured" in report.inconclusive_reasons


def test_live_status_policy_treats_budget_skipped_required_coverage_as_warning() -> None:
    status = RadarBenchmarkEvaluationPolicy().status(
        evaluation_mode="live",
        missing=["intent-family:limitationCritique"],
        noise_hits=[],
        leaks=[],
        warnings=[],
        skipped_required=[
            {
                "kind": "queryFamily",
                "value": "limitationCritique",
                "reason": "budget-max-external-queries",
                "intentId": "intent-limitation",
            }
        ],
        inconclusive=[],
        provider_health="ok",
    )

    assert status == "warning"


def test_benchmark_coverage_and_trace_policies_are_component_owned() -> None:
    scenario = _scenario()
    run, _found_materials = _recorded_run()

    assert RadarBenchmarkTracePolicy().provider_health(run) == "ok"
    coverage = RadarBenchmarkCoveragePolicy().coverage(
        scenario=scenario,
        intent_families={"broadDiscovery", "caseExample"},
        evidence_types={"overview", "caseExample"},
        selected_domains={"example.com"},
        trace_complete=True,
    )

    assert "benchmarkPaper" in coverage["queryFamilies"]["missing"]
    assert coverage["domains"]["covered"] == ["example.com"]


def test_external_run_attaches_live_benchmark_report_for_matching_scenario() -> None:
    scenario = _scenario()
    result = _run_external_service(scenario.workspace())

    report = result["run"]["benchmarkReport"]

    assert report["scenarioId"] == scenario.id
    assert report["evaluationMode"] == "live"
    assert report["status"] == "warning"
    assert report["providerHealth"] == "ok"
    assert report["plannedCoverage"]["queryFamilies"]["missing"] == []
    assert "limitationCritique" in report["executedCoverage"]["queryFamilies"]["missing"]
    assert any(item["value"] == "limitationCritique" for item in report["skippedRequiredCoverage"])
    json.dumps(result)


def test_external_run_does_not_attach_report_for_non_matching_radar() -> None:
    scenario = _scenario()
    workspace = scenario.workspace()
    workspace["projectProfile"]["id"] = "different-project"

    result = _run_external_service(workspace)

    assert "benchmarkReport" not in result["run"]


def test_disabled_provider_external_run_attaches_inconclusive_report() -> None:
    scenario = _scenario()
    result = _run_external_service(
        scenario.workspace(),
        settings=BackendSettings(
            _env_file=None,
            OPENROUTER_API_KEY="recorded-token",
            OPENROUTER_DEFAULT_MODEL="recorded-model",
            OPENROUTER_WEB_TOOLS_ENABLED=False,
            OPENROUTER_WEB_SEARCH_MODEL="recorded-model",
            DRAFT_RUN_EXECUTION_MODE="standard",
        ),
    )

    report = result["run"]["benchmarkReport"]

    assert report["status"] == "inconclusive"
    assert report["providerHealth"] == "unavailable"
    assert "openrouter-web-tools-disabled" in report["inconclusiveReasons"]


def _scenario():
    return get_golden_radar_benchmark_scenarios()[0]


def _recorded_run() -> tuple[dict, list[dict]]:
    # Re-run through the service so the evaluator receives the same shape as live code,
    # while avoiding the report field itself in the payload under test.
    result = _run_external_service(_scenario().workspace())
    run = deepcopy(result["run"])
    run.pop("benchmarkReport", None)
    return run, deepcopy(result["foundMaterials"])


def _run_external_service(workspace: dict, settings: BackendSettings | None = None) -> dict:
    fixture = RecordedRadarFixture.load("benchmark-industrial-ai-maintenance-cases.json")
    service = UpstreamRadarExternalRunService(
        settings=settings
        or BackendSettings(
            _env_file=None,
            OPENROUTER_API_KEY="recorded-token",
            OPENROUTER_DEFAULT_MODEL="recorded-model",
            OPENROUTER_WEB_TOOLS_ENABLED=True,
            OPENROUTER_WEB_SEARCH_MODEL="recorded-model",
            DRAFT_RUN_EXECUTION_MODE="standard",
        ),
        web_search_adapter=RecordedRadarSearchAdapter(fixture),
        url_reader=RecordedUrlReader(fixture),
        openrouter_validator=OpenRouterConfigValidator(),
    )
    return service.run(workspace=workspace, radar_id=_scenario().radar_id)


def _add_executed_query(run: dict, *, family: str, evidence_type: str) -> None:
    plan = run["searchPlan"]
    intent = next(item for item in plan["intents"] if item["family"] == family)
    query = {
        "id": f"query-added-{family}",
        "intentId": intent["id"],
        "sourceHandleId": intent["sourceHandleId"],
        "intent": intent["intentType"],
        "family": family,
        "evidenceType": evidence_type,
        "priority": intent["priority"],
        "label": intent["label"],
        "query": " ".join(intent["queryTerms"]),
        "rationale": intent["rationale"],
    }
    plan["queries"].append(query)
    plan["skippedIntentDetails"] = [
        item for item in plan["skippedIntentDetails"] if item.get("family") != family
    ]
    plan["skippedIntents"] = [
        item for item in plan["skippedIntents"] if f"family={family}" not in str(item)
    ]
    run["operations"].append(
        {
            "id": f"{run['id']}-search-{query['id']}",
            "runId": run["id"],
            "sourceHandleId": query["sourceHandleId"],
            "kind": "openWebQuery",
            "label": query["label"],
            "status": "succeeded",
            "startedAt": run["startedAt"],
            "completedAt": run["completedAt"],
            "target": query["query"],
            "foundMaterialIds": [],
        }
    )
    run["rawResults"].append(
        {
            "id": f"{run['id']}-raw-{query['id']}-1",
            "sourceHandleId": query["sourceHandleId"],
            "queryId": query["id"],
            "title": f"{family} result",
            "url": f"https://{family.lower()}.example/source",
            "snippet": f"{family} evidence for industrial maintenance.",
            "domain": f"{family.lower()}.example",
            "score": 80,
            "duplicateKey": f"{family.lower()}.example/source",
            "provider": "recorded",
        }
    )
