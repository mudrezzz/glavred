"""Owner: upstream.application

Used by: recorded upstream Radar benchmark tests and developer diagnostics.
Does not own: live provider transport, API routing, UI rendering, signal scoring, or DraftRun.
Architecture doc: docs/architecture/UPSTREAM_SEARCH_AND_SIGNAL_ARCHITECTURE.md
"""

from __future__ import annotations

from typing import Any

from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings
from backend.app.upstream.application.benchmark.recorded_adapters import (
    RecordedRadarFixture,
    RecordedRadarSearchAdapter,
    RecordedUrlReader,
)
from backend.app.upstream.application.benchmark.scenarios import (
    RadarBenchmarkReport,
    RadarBenchmarkScenario,
    get_golden_radar_benchmark_scenarios,
)
from backend.app.upstream.application.external_run_service import UpstreamRadarExternalRunService


class RadarBenchmarkRunner:
    def run(self, scenario: RadarBenchmarkScenario) -> RadarBenchmarkReport:
        fixture = RecordedRadarFixture.load(f"{scenario.id}.json")
        workspace = scenario.workspace()
        service = UpstreamRadarExternalRunService(
            settings=BackendSettings(
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
        result = service.run(workspace=workspace, radar_id=scenario.radar_id)
        return self._report(scenario=scenario, workspace=workspace, result=result)

    def _report(
        self,
        *,
        scenario: RadarBenchmarkScenario,
        workspace: dict[str, Any],
        result: dict[str, Any],
    ) -> RadarBenchmarkReport:
        run = result["run"]
        found_materials = result["foundMaterials"]
        search_plan = run.get("searchPlan", {})
        raw_results = run.get("rawResults", [])
        selected = run.get("selectedForRead", [])
        rejected = run.get("rejectedBeforeRead", [])
        intent_families = {str(item.get("family")) for item in search_plan.get("intents", [])}
        evidence_types = {str(item.get("evidenceType")) for item in search_plan.get("intents", [])}
        selected_domains = {self._domain(str(item.get("url") or "")) for item in selected}
        missing = self._missing_expectations(
            scenario=scenario,
            intent_families=intent_families,
            evidence_types=evidence_types,
            raw_results=raw_results,
            selected=selected,
            found_materials=found_materials,
            selected_domains=selected_domains,
        )
        trace_complete = self._trace_complete(run)
        if not trace_complete:
            missing.append("trace-completeness")
        noise_hits = self._accepted_noise_hits(scenario=scenario, found_materials=found_materials)
        leaks = self._downstream_leaks(workspace=workspace, result=result)
        counters = {
            "intentCount": len(search_plan.get("intents", [])),
            "queryCount": len(search_plan.get("queries", [])),
            "rawResultCount": len(raw_results),
            "selectedReadCount": len(selected),
            "rejectedBeforeReadCount": len(rejected),
            "foundMaterialCount": len(found_materials),
            "distinctSelectedDomainCount": len(selected_domains),
        }
        status = "passed" if not missing and not noise_hits and not leaks else "failed"
        warnings = []
        if scenario.optional_intent_families and not set(scenario.optional_intent_families).issubset(intent_families):
            warnings.append("optional-intent-family-not-covered")
        return RadarBenchmarkReport(
            scenario_id=scenario.id,
            status=status,
            counters=counters,
            missing_expectations=missing,
            warnings=warnings,
            unacceptable_noise_hits=noise_hits,
            downstream_leaks=leaks,
            trace_complete=trace_complete,
            run=run,
            found_materials=found_materials,
        )

    def _missing_expectations(
        self,
        *,
        scenario: RadarBenchmarkScenario,
        intent_families: set[str],
        evidence_types: set[str],
        raw_results: list[dict[str, Any]],
        selected: list[dict[str, Any]],
        found_materials: list[dict[str, Any]],
        selected_domains: set[str],
    ) -> list[str]:
        missing = [
            f"intent-family:{family}"
            for family in scenario.expected_intent_families
            if family not in intent_families
        ]
        missing.extend(
            f"evidence-type:{evidence_type}"
            for evidence_type in scenario.expected_evidence_types
            if evidence_type not in evidence_types
        )
        thresholds = {
            "raw-results": (len(raw_results), scenario.minimum_raw_results),
            "selected-reads": (len(selected), scenario.minimum_selected_reads),
            "found-materials": (len(found_materials), scenario.minimum_found_materials),
            "distinct-domains": (len(selected_domains), scenario.minimum_distinct_domains),
        }
        missing.extend(f"{name}:{actual}/{expected}" for name, (actual, expected) in thresholds.items() if actual < expected)
        return missing

    def _accepted_noise_hits(
        self,
        *,
        scenario: RadarBenchmarkScenario,
        found_materials: list[dict[str, Any]],
    ) -> list[str]:
        hits = []
        for material in found_materials:
            text = f"{material.get('title', '')} {material.get('snippet', '')} {material.get('summary', '')}".lower()
            if any(term in text for term in scenario.unacceptable_noise_terms):
                hits.append(str(material.get("id") or material.get("title") or "found-material"))
        return hits

    def _downstream_leaks(self, *, workspace: dict[str, Any], result: dict[str, Any]) -> list[str]:
        leaks = []
        if result.get("sourceSignals"):
            leaks.append("sourceSignals")
        if result.get("postCandidates"):
            leaks.append("postCandidates")
        if result.get("draftRuns"):
            leaks.append("draftRuns")
        for key in ("sourceSignals", "postCandidates", "contentPlanItems", "draftRuns"):
            if workspace.get(key):
                leaks.append(f"workspace-input:{key}")
        return leaks

    def _trace_complete(self, run: dict[str, Any]) -> bool:
        plan = run.get("searchPlan", {})
        return all(
            [
                bool(plan.get("intents")),
                bool(plan.get("queries")),
                bool(plan.get("trace", {}).get("intentCoverage")),
                bool(run.get("rawResults")),
                bool(run.get("selectedForRead")),
                "rejectedBeforeRead" in run,
                bool(run.get("foundMaterialIds")),
            ]
        )

    def _domain(self, url: str) -> str:
        return url.split("/")[2] if "://" in url else url


def run_radar_benchmark(scenario_id: str) -> RadarBenchmarkReport:
    scenarios = {scenario.id: scenario for scenario in get_golden_radar_benchmark_scenarios()}
    if scenario_id not in scenarios:
        raise ValueError(f"Unknown radar benchmark scenario: {scenario_id}")
    return RadarBenchmarkRunner().run(scenarios[scenario_id])


__all__ = ("RadarBenchmarkRunner", "get_golden_radar_benchmark_scenarios", "run_radar_benchmark")
