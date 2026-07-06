"""Owner: drafting.application.operations

Used by: Validation loops to normalize stop reasons and budget-denial incidents.
Does not own: Runtime counters, provider calls, prompt text, or persistence.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from typing import Any, Mapping

from backend.app.drafting.application.operations.validation_runtime_budget_contracts import (
    CANONICAL_STOP_REASONS,
    STOP_ACCEPTED_QUALITY,
    STOP_BUDGET_EXHAUSTED,
    STOP_HUMAN_REVIEW_REQUIRED,
    STOP_MAX_ITERATIONS,
    STOP_NO_IMPROVEMENT,
    STOP_PROVIDER_INCIDENT,
)


class ValidationStopReasonPolicy:
    def normalize(self, reason: str | None) -> str:
        value = str(reason or "").strip()
        if value in CANONICAL_STOP_REASONS:
            return value
        if value in {"validator-clean", "editorially-improved", "final-quality-gate-passed", "final-quality-repair-accepted"}:
            return STOP_ACCEPTED_QUALITY
        if value in {"max-iterations"}:
            return STOP_MAX_ITERATIONS
        if value in {"no-fresh-angle", "consecutive-non-improving-attempts", "max-consecutive-non-improving-attempts"}:
            return STOP_NO_IMPROVEMENT
        if value in {"provider-failed", "operation-failed", "provider-unconfigured", "not-run"}:
            return STOP_PROVIDER_INCIDENT
        if value in {"budget-exhausted", "max-wall-clock-seconds", "max-llm-calls", "max-revision-cycles", "max-pairwise-rounds", "max-final-gate-repair-cycles"}:
            return STOP_BUDGET_EXHAUSTED
        if value in {"no-final-candidate", "quality-blocked", "blocked"}:
            return STOP_HUMAN_REVIEW_REQUIRED
        return STOP_HUMAN_REVIEW_REQUIRED if not value else STOP_NO_IMPROVEMENT

    def final_validation_stop_reason(
        self,
        *,
        final_candidate: Mapping[str, Any] | None,
        loop_stop_reason: str,
        runtime_stop_reason: str | None,
        final_gate: Mapping[str, Any],
    ) -> str:
        if runtime_stop_reason == STOP_BUDGET_EXHAUSTED:
            return runtime_stop_reason
        if final_candidate and final_gate.get("status") in {"passed", "warning", "critical"}:
            return STOP_ACCEPTED_QUALITY
        if final_candidate:
            return self.normalize(loop_stop_reason)
        return self.normalize(runtime_stop_reason or STOP_HUMAN_REVIEW_REQUIRED)

    def finalize_revision_loop_stop(
        self,
        guard: Any | None,
        stop_reason: str,
        detail_stop_reason: str | None,
    ) -> tuple[str, str | None, dict[str, Any]]:
        canonical = self.normalize(guard.stop_reason if guard and guard.stop_reason else stop_reason)
        detail = detail_stop_reason
        if canonical != stop_reason:
            detail = detail or stop_reason
        if guard:
            guard.record_stop(canonical, detail=detail)
            return canonical, detail, guard.snapshot()
        return canonical, detail, {}


class ValidationRuntimeBudgetIncidentFactory:
    def operation_denied(
        self,
        progress: Any,
        *,
        kind: str,
        operation_id: str,
        detail: str,
    ) -> bool:
        guard = getattr(progress, "runtime_guard", None) if progress else None
        if guard:
            denial_reason = guard.denial_reason(kind, operation_id)
            if not denial_reason:
                return False
            stop_reason = ValidationStopReasonPolicy().normalize(denial_reason)
            stop_detail = denial_reason if stop_reason != STOP_BUDGET_EXHAUSTED else detail
            guard.record_stop(stop_reason, detail=stop_detail)
            return True
        return False
