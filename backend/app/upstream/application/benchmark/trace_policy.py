"""Owner: upstream.application

Used by: Radar benchmark evaluator.
Does not own: provider transport, API routing, UI rendering, signal scoring, or DraftRun.
Architecture doc: docs/architecture/UPSTREAM_SEARCH_AND_SIGNAL_ARCHITECTURE.md
"""

from __future__ import annotations

from typing import Any

from backend.app.upstream.application.benchmark.scenarios import (
    BenchmarkEvaluationMode,
    BenchmarkProviderHealth,
)


class RadarBenchmarkTracePolicy:
    def trace_complete(self, run: dict[str, Any]) -> bool:
        plan = run.get("searchPlan", {}) if isinstance(run.get("searchPlan"), dict) else {}
        base_complete = all(
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
        triage = run.get("searchTriage") if isinstance(run.get("searchTriage"), dict) else None
        if not triage:
            return base_complete
        read_plan = triage.get("readPlan") if isinstance(triage.get("readPlan"), dict) else {}
        decisions = read_plan.get("decisions") if isinstance(read_plan.get("decisions"), list) else []
        outcomes = triage.get("readOutcomes") if isinstance(triage.get("readOutcomes"), list) else []
        selected_count = sum(
            1 for item in decisions if isinstance(item, dict) and item.get("status") == "selected"
        )
        return base_complete and len(decisions) == len(run.get("rawResults", [])) and len(outcomes) == selected_count

    def provider_health(self, run: dict[str, Any]) -> BenchmarkProviderHealth:
        operations = [item for item in run.get("operations", []) if isinstance(item, dict)]
        search_operations = [item for item in operations if item.get("kind") == "openWebQuery"]
        if not search_operations:
            return "unavailable"
        failures = [item for item in search_operations if item.get("status") in {"failed", "skipped"}]
        if len(failures) == len(search_operations):
            return "unavailable"
        return "degraded" if failures else "ok"

    def inconclusive_reasons(
        self,
        *,
        run: dict[str, Any],
        provider_health: BenchmarkProviderHealth,
        evaluation_mode: BenchmarkEvaluationMode,
    ) -> list[str]:
        if evaluation_mode != "live" or provider_health != "unavailable":
            return []
        reasons = []
        operations = [item for item in run.get("operations", []) if isinstance(item, dict)]
        search_operations = [item for item in operations if item.get("kind") == "openWebQuery"]
        for operation in search_operations:
            reason = str(operation.get("skippedReason") or operation.get("error") or "")
            if reason:
                reasons.append(reason)
        reasons.append("provider-search-unavailable")
        if not run.get("rawResults"):
            reasons.append("no-live-raw-results")
        if not run.get("searchPlan"):
            reasons.append("missing-search-plan")
        return list(dict.fromkeys(reasons))
