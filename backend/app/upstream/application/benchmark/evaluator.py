"""Owner: upstream.application

Used by: recorded and live Radar benchmark evaluation.
Does not own: provider transport, API routing, UI rendering, signal scoring, or DraftRun.
Architecture doc: docs/architecture/UPSTREAM_SEARCH_AND_SIGNAL_ARCHITECTURE.md
"""

from __future__ import annotations

from typing import Any

from backend.app.upstream.application.benchmark.evaluation_policy import RadarBenchmarkEvaluationPolicy
from backend.app.upstream.application.benchmark.scenarios import (
    BenchmarkEvaluationMode,
    RadarBenchmarkReport,
    RadarBenchmarkScenario,
)


class RadarBenchmarkEvaluator:
    def __init__(self, policy: RadarBenchmarkEvaluationPolicy | None = None) -> None:
        self._policy = policy or RadarBenchmarkEvaluationPolicy()

    def evaluate(
        self,
        *,
        scenario: RadarBenchmarkScenario,
        run: dict[str, Any],
        found_materials: list[dict[str, Any]],
        workspace: dict[str, Any] | None = None,
        result: dict[str, Any] | None = None,
        evaluation_mode: BenchmarkEvaluationMode = "recorded",
    ) -> RadarBenchmarkReport:
        search_plan = run.get("searchPlan", {}) if isinstance(run.get("searchPlan"), dict) else {}
        raw_results = run.get("rawResults", []) if isinstance(run.get("rawResults"), list) else []
        selected = run.get("selectedForRead", []) if isinstance(run.get("selectedForRead"), list) else []
        rejected = run.get("rejectedBeforeRead", []) if isinstance(run.get("rejectedBeforeRead"), list) else []
        planned_intents = [item for item in search_plan.get("intents", []) if isinstance(item, dict)]
        planned_families = {str(item.get("family")) for item in planned_intents if item.get("family")}
        planned_evidence_types = {str(item.get("evidenceType")) for item in planned_intents if item.get("evidenceType")}
        executed_query_ids = self._executed_query_ids(search_plan=search_plan, run=run, raw_results=raw_results)
        executed_queries = [
            item
            for item in search_plan.get("queries", [])
            if isinstance(item, dict) and str(item.get("id") or "") in executed_query_ids
        ]
        executed_families = {str(item.get("family")) for item in executed_queries if item.get("family")}
        executed_evidence_types = {str(item.get("evidenceType")) for item in executed_queries if item.get("evidenceType")}
        evaluation_families = executed_families if evaluation_mode == "live" else planned_families
        evaluation_evidence_types = executed_evidence_types if evaluation_mode == "live" else planned_evidence_types
        selected_domains = {self._domain(str(item.get("url") or "")) for item in selected if isinstance(item, dict)}
        missing = self._policy.missing_expectations(
            scenario=scenario,
            intent_families=evaluation_families,
            evidence_types=evaluation_evidence_types,
            raw_results=raw_results,
            selected=selected,
            found_materials=found_materials,
            selected_domains=selected_domains,
        )
        trace_complete = self._policy.trace_complete(run)
        if not trace_complete:
            missing.append("trace-completeness")
        noise_hits = self._policy.accepted_noise_hits(scenario=scenario, found_materials=found_materials)
        leaks = self._policy.downstream_leaks(workspace=workspace or {}, result=result or {}) if evaluation_mode == "recorded" else []
        warnings = []
        optional_base_families = executed_families if evaluation_mode == "live" else planned_families
        optional_missing = sorted(set(scenario.optional_intent_families).difference(optional_base_families))
        if optional_missing:
            warnings.append("optional-intent-family-not-covered")
        provider_health = self._policy.provider_health(run)
        inconclusive = self._policy.inconclusive_reasons(
            run=run,
            provider_health=provider_health,
            evaluation_mode=evaluation_mode,
        )
        missing_families = set(scenario.expected_intent_families).difference(executed_families)
        missing_evidence_types = set(scenario.expected_evidence_types).difference(executed_evidence_types)
        skipped_required = (
            self._policy.skipped_required_coverage(
                scenario=scenario,
                missing_families=missing_families,
                missing_evidence_types=missing_evidence_types,
                skipped_intents=search_plan.get("skippedIntentDetails", []),
                planned_intents=planned_intents,
            )
            if evaluation_mode == "live"
            else []
        )
        status = self._policy.status(
            evaluation_mode=evaluation_mode,
            missing=missing,
            noise_hits=noise_hits,
            leaks=leaks,
            warnings=warnings,
            skipped_required=skipped_required,
            inconclusive=inconclusive,
            provider_health=provider_health,
        )
        counters = {
            "intentCount": len(search_plan.get("intents", [])),
            "queryCount": len(search_plan.get("queries", [])),
            "rawResultCount": len(raw_results),
            "selectedReadCount": len(selected),
            "rejectedBeforeReadCount": len(rejected),
            "foundMaterialCount": len(found_materials),
            "distinctSelectedDomainCount": len(selected_domains),
        }
        return RadarBenchmarkReport(
            scenario_id=scenario.id,
            status=status,
            evaluation_mode=evaluation_mode,
            provider_health=provider_health,
            coverage=self._policy.coverage(
                scenario=scenario,
                intent_families=planned_families,
                evidence_types=planned_evidence_types,
                selected_domains=selected_domains,
                trace_complete=trace_complete,
            ),
            planned_coverage=self._policy.coverage(
                scenario=scenario,
                intent_families=planned_families,
                evidence_types=planned_evidence_types,
                selected_domains=selected_domains,
                trace_complete=trace_complete,
            ),
            executed_coverage=self._policy.coverage(
                scenario=scenario,
                intent_families=executed_families,
                evidence_types=executed_evidence_types,
                selected_domains=selected_domains,
                trace_complete=trace_complete,
            ),
            skipped_required_coverage=skipped_required,
            counters=counters,
            missing_expectations=missing,
            warnings=warnings,
            unacceptable_noise_hits=noise_hits,
            inconclusive_reasons=inconclusive,
            downstream_leaks=leaks,
            trace_complete=trace_complete,
            run=run,
            found_materials=found_materials,
        )

    def _domain(self, url: str) -> str:
        return url.split("/")[2] if "://" in url else url

    def _executed_query_ids(
        self,
        *,
        search_plan: dict[str, Any],
        run: dict[str, Any],
        raw_results: list[dict[str, Any]],
    ) -> set[str]:
        queries = [item for item in search_plan.get("queries", []) if isinstance(item, dict)]
        succeeded_targets = {
            str(operation.get("target") or "")
            for operation in run.get("operations", [])
            if isinstance(operation, dict)
            and operation.get("kind") == "openWebQuery"
            and operation.get("status") == "succeeded"
        }
        executed = {
            str(query.get("id") or "")
            for query in queries
            if str(query.get("query") or "") in succeeded_targets
        }
        executed.update(str(item.get("queryId") or "") for item in raw_results if isinstance(item, dict))
        return {item for item in executed if item}


def evaluate_live_radar_run(
    *,
    scenario: RadarBenchmarkScenario,
    run: dict[str, Any],
    found_materials: list[dict[str, Any]],
) -> RadarBenchmarkReport:
    return RadarBenchmarkEvaluator().evaluate(
        scenario=scenario,
        run=run,
        found_materials=found_materials,
        evaluation_mode="live",
    )


__all__ = ("RadarBenchmarkEvaluator", "evaluate_live_radar_run")
