"""Owner: upstream.application

Used by: RadarBenchmarkEvaluator.
Does not own: provider transport, API routing, UI rendering, signal scoring, or DraftRun.
Architecture doc: docs/architecture/UPSTREAM_SEARCH_AND_SIGNAL_ARCHITECTURE.md
"""

from __future__ import annotations

from typing import Any

from backend.app.upstream.application.benchmark.coverage_policy import RadarBenchmarkCoveragePolicy
from backend.app.upstream.application.benchmark.expectation_policy import RadarBenchmarkExpectationPolicy
from backend.app.upstream.application.benchmark.scenarios import (
    BenchmarkEvaluationMode,
    BenchmarkProviderHealth,
    BenchmarkStatus,
    RadarBenchmarkScenario,
)
from backend.app.upstream.application.benchmark.trace_policy import RadarBenchmarkTracePolicy


class RadarBenchmarkEvaluationPolicy:
    def __init__(
        self,
        *,
        expectations: RadarBenchmarkExpectationPolicy | None = None,
        coverage: RadarBenchmarkCoveragePolicy | None = None,
        trace: RadarBenchmarkTracePolicy | None = None,
    ) -> None:
        self._expectations = expectations or RadarBenchmarkExpectationPolicy()
        self._coverage = coverage or RadarBenchmarkCoveragePolicy()
        self._trace = trace or RadarBenchmarkTracePolicy()

    def status(
        self,
        *,
        evaluation_mode: BenchmarkEvaluationMode,
        missing: list[str],
        noise_hits: list[str],
        leaks: list[str],
        warnings: list[str],
        skipped_required: list[dict[str, Any]],
        inconclusive: list[str],
        provider_health: BenchmarkProviderHealth,
    ) -> BenchmarkStatus:
        if evaluation_mode == "live" and inconclusive:
            return "inconclusive"
        if evaluation_mode == "live":
            hard_missing = [item for item in missing if not self._covered_by_skipped_required(item, skipped_required)]
            if noise_hits or leaks or hard_missing:
                return "failed"
            if skipped_required:
                return "warning"
        elif noise_hits or leaks or missing:
            return "failed"
        if warnings or provider_health == "degraded":
            return "warning"
        return "passed"

    def missing_expectations(
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
        return self._expectations.missing_expectations(
            scenario=scenario,
            intent_families=intent_families,
            evidence_types=evidence_types,
            raw_results=raw_results,
            selected=selected,
            found_materials=found_materials,
            selected_domains=selected_domains,
        )

    def accepted_noise_hits(self, *, scenario: RadarBenchmarkScenario, found_materials: list[dict[str, Any]]) -> list[str]:
        return self._expectations.accepted_noise_hits(scenario=scenario, found_materials=found_materials)

    def downstream_leaks(self, *, workspace: dict[str, Any], result: dict[str, Any]) -> list[str]:
        return self._expectations.downstream_leaks(workspace=workspace, result=result)

    def trace_complete(self, run: dict[str, Any]) -> bool:
        return self._trace.trace_complete(run)

    def provider_health(self, run: dict[str, Any]) -> BenchmarkProviderHealth:
        return self._trace.provider_health(run)

    def inconclusive_reasons(
        self,
        *,
        run: dict[str, Any],
        provider_health: BenchmarkProviderHealth,
        evaluation_mode: BenchmarkEvaluationMode,
    ) -> list[str]:
        return self._trace.inconclusive_reasons(
            run=run,
            provider_health=provider_health,
            evaluation_mode=evaluation_mode,
        )

    def coverage(
        self,
        *,
        scenario: RadarBenchmarkScenario,
        intent_families: set[str],
        evidence_types: set[str],
        selected_domains: set[str],
        trace_complete: bool,
    ) -> dict[str, Any]:
        return self._coverage.coverage(
            scenario=scenario,
            intent_families=intent_families,
            evidence_types=evidence_types,
            selected_domains=selected_domains,
            trace_complete=trace_complete,
        )

    def skipped_required_coverage(
        self,
        *,
        scenario: RadarBenchmarkScenario,
        missing_families: set[str],
        missing_evidence_types: set[str],
        skipped_intents: list[dict[str, Any]],
        planned_intents: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        return self._coverage.skipped_required_coverage(
            scenario=scenario,
            missing_families=missing_families,
            missing_evidence_types=missing_evidence_types,
            skipped_intents=skipped_intents,
            planned_intents=planned_intents,
        )

    def _covered_by_skipped_required(self, missing_item: str, skipped_required: list[dict[str, Any]]) -> bool:
        if ":" not in missing_item:
            return False
        prefix, value = missing_item.split(":", 1)
        kind = {"intent-family": "queryFamily", "evidence-type": "evidenceType"}.get(prefix)
        return any(item.get("kind") == kind and item.get("value") == value for item in skipped_required)
