"""Owner: drafting.application.operations

Used by: DraftRun validation/revision runtime to keep long background loops bounded.
Does not own: provider adapters, prompt text, SQLite persistence, UI rendering.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Callable, Mapping

from backend.app.domain.draft_run_budget import DraftRunExecutionMode

STOP_ACCEPTED_QUALITY = "acceptedQuality"
STOP_HUMAN_REVIEW_REQUIRED = "humanReviewRequired"
STOP_BUDGET_EXHAUSTED = "budgetExhausted"
STOP_MAX_ITERATIONS = "maxIterations"
STOP_NO_IMPROVEMENT = "noImprovement"
STOP_PROVIDER_INCIDENT = "providerIncident"

CANONICAL_STOP_REASONS = {
    STOP_ACCEPTED_QUALITY,
    STOP_HUMAN_REVIEW_REQUIRED,
    STOP_BUDGET_EXHAUSTED,
    STOP_MAX_ITERATIONS,
    STOP_NO_IMPROVEMENT,
    STOP_PROVIDER_INCIDENT,
}

PROVIDER_HEAVY_OPERATION_KINDS = {
    "llmValidation",
    "editorialCritique",
    "alternativeAngle",
    "alternativeAngleCandidate",
    "pairwiseRanking",
    "directedRevision",
    "finalQualityGate",
}


@dataclass(frozen=True)
class ValidationRuntimeBudgetProfile:
    profile_id: str
    execution_mode: str
    max_wall_clock_seconds: int
    max_llm_calls: int
    max_revision_cycles: int
    max_pairwise_rounds: int
    max_final_gate_repair_cycles: int
    max_consecutive_non_improving_attempts: int
    stale_after_seconds: int
    long_operation_warning_seconds: int

    def to_payload(self) -> dict[str, Any]:
        return {
            "profileId": self.profile_id,
            "executionMode": self.execution_mode,
            "maxWallClockSeconds": self.max_wall_clock_seconds,
            "maxLlmCalls": self.max_llm_calls,
            "maxRevisionCycles": self.max_revision_cycles,
            "maxPairwiseRounds": self.max_pairwise_rounds,
            "maxFinalGateRepairCycles": self.max_final_gate_repair_cycles,
            "maxConsecutiveNonImprovingAttempts": self.max_consecutive_non_improving_attempts,
            "staleAfterSeconds": self.stale_after_seconds,
            "longOperationWarningSeconds": self.long_operation_warning_seconds,
        }


class ValidationRuntimeBudgetPolicy:
    _DEFAULTS = {
        DraftRunExecutionMode.SMOKE.value: ValidationRuntimeBudgetProfile(
            "validationLoop:smoke", DraftRunExecutionMode.SMOKE.value, 300, 8, 1, 2, 1, 1, 180, 60
        ),
        DraftRunExecutionMode.STANDARD.value: ValidationRuntimeBudgetProfile(
            "validationLoop:standard", DraftRunExecutionMode.STANDARD.value, 2400, 24, 3, 4, 2, 2, 900, 300
        ),
        DraftRunExecutionMode.FULL.value: ValidationRuntimeBudgetProfile(
            "validationLoop:full", DraftRunExecutionMode.FULL.value, 3600, 40, 5, 6, 3, 3, 1200, 600
        ),
    }

    def profile_for(
        self,
        context_artifact: Mapping[str, Any] | None = None,
        *,
        execution_mode: str | None = None,
        max_revision_iterations: int | None = None,
        max_final_repair_iterations: int | None = None,
    ) -> ValidationRuntimeBudgetProfile:
        mode = execution_mode or _execution_mode_from_context(context_artifact)
        base = self._DEFAULTS.get(mode, self._DEFAULTS[DraftRunExecutionMode.STANDARD.value])
        revision_cap = _positive_int(max_revision_iterations)
        final_repair_cap = _positive_int(max_final_repair_iterations)
        if revision_cap is None and final_repair_cap is None:
            return base
        return ValidationRuntimeBudgetProfile(
            profile_id=base.profile_id,
            execution_mode=base.execution_mode,
            max_wall_clock_seconds=base.max_wall_clock_seconds,
            max_llm_calls=base.max_llm_calls,
            max_revision_cycles=min(base.max_revision_cycles, revision_cap) if revision_cap else base.max_revision_cycles,
            max_pairwise_rounds=base.max_pairwise_rounds,
            max_final_gate_repair_cycles=min(base.max_final_gate_repair_cycles, final_repair_cap) if final_repair_cap else base.max_final_gate_repair_cycles,
            max_consecutive_non_improving_attempts=base.max_consecutive_non_improving_attempts,
            stale_after_seconds=base.stale_after_seconds,
            long_operation_warning_seconds=base.long_operation_warning_seconds,
        )


@dataclass
class ValidationRuntimeCounters:
    llm_calls: int = 0
    revision_cycles: int = 0
    pairwise_rounds: int = 0
    final_gate_repair_cycles: int = 0
    consecutive_non_improving_attempts: int = 0

    def to_payload(self) -> dict[str, int]:
        return {
            "llmCalls": self.llm_calls,
            "revisionCycles": self.revision_cycles,
            "pairwiseRounds": self.pairwise_rounds,
            "finalGateRepairCycles": self.final_gate_repair_cycles,
            "consecutiveNonImprovingAttempts": self.consecutive_non_improving_attempts,
        }


class ValidationRuntimeGuard:
    def __init__(
        self,
        profile: ValidationRuntimeBudgetProfile,
        *,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.profile = profile
        self._now = now or (lambda: datetime.now(UTC))
        self.started_at = self._now()
        self.last_heartbeat_at = self.started_at
        self.current_operation_id: str | None = None
        self.current_operation_started_at: datetime | None = None
        self.counters = ValidationRuntimeCounters()
        self.stop_reason: str | None = None
        self.detail_stop_reason: str | None = None
        self.incidents: list[dict[str, Any]] = []

    def can_start_operation(self, kind: str, operation_id: str | None = None) -> bool:
        return self._denial_reason(kind, operation_id) is None

    def start_operation(self, operation_id: str, kind: str) -> bool:
        denial = self._denial_reason(kind, operation_id)
        self.last_heartbeat_at = self._now()
        if denial:
            self.record_stop(STOP_BUDGET_EXHAUSTED, detail=denial)
            self.incidents.append({"type": STOP_BUDGET_EXHAUSTED, "operationId": operation_id, "kind": kind, "reason": denial})
            return False
        self.current_operation_id = operation_id
        self.current_operation_started_at = self.last_heartbeat_at
        self._increment(kind, operation_id)
        return True

    def complete_operation(self, operation_id: str) -> None:
        self.last_heartbeat_at = self._now()
        if self.current_operation_id == operation_id:
            self.current_operation_id = None
            self.current_operation_started_at = None

    def fail_operation(self, operation_id: str, error: str | None = None) -> None:
        self.last_heartbeat_at = self._now()
        self.record_stop(STOP_PROVIDER_INCIDENT, detail=error or "operation-failed")
        self.incidents.append({"type": STOP_PROVIDER_INCIDENT, "operationId": operation_id, "safeError": error})
        if self.current_operation_id == operation_id:
            self.current_operation_id = None
            self.current_operation_started_at = None

    def heartbeat(self) -> None:
        self.last_heartbeat_at = self._now()

    def record_revision_outcome(self, *, accepted: bool) -> None:
        self.last_heartbeat_at = self._now()
        if accepted:
            self.counters.consecutive_non_improving_attempts = 0
            return
        self.counters.consecutive_non_improving_attempts += 1
        if self.counters.consecutive_non_improving_attempts >= self.profile.max_consecutive_non_improving_attempts:
            self.record_stop(STOP_NO_IMPROVEMENT, detail="consecutive-non-improving-attempts")

    def record_stop(self, stop_reason: str, *, detail: str | None = None) -> str:
        canonical = normalize_validation_stop_reason(stop_reason)
        if self.stop_reason is None or canonical in {STOP_BUDGET_EXHAUSTED, STOP_PROVIDER_INCIDENT}:
            self.stop_reason = canonical
        if detail:
            self.detail_stop_reason = detail
        return self.stop_reason

    @property
    def exhausted(self) -> bool:
        return self.stop_reason == STOP_BUDGET_EXHAUSTED

    def snapshot(self) -> dict[str, Any]:
        now = self._now()
        current_age = (now - self.current_operation_started_at).total_seconds() if self.current_operation_started_at else 0
        return {
            "profileId": self.profile.profile_id,
            "executionMode": self.profile.execution_mode,
            "limits": self.profile.to_payload(),
            "used": self.counters.to_payload(),
            "startedAt": self.started_at.isoformat(),
            "lastHeartbeatAt": self.last_heartbeat_at.isoformat(),
            "currentOperationId": self.current_operation_id,
            "currentOperationStartedAt": self.current_operation_started_at.isoformat() if self.current_operation_started_at else None,
            "slowButHealthy": bool(self.current_operation_id and current_age <= self.profile.stale_after_seconds),
            "stopReason": self.stop_reason,
            "detailStopReason": self.detail_stop_reason,
            "exhausted": self.exhausted,
            "incidents": [dict(item) for item in self.incidents],
        }

    def _denial_reason(self, kind: str, operation_id: str | None) -> str | None:
        elapsed = (self._now() - self.started_at).total_seconds()
        if elapsed > self.profile.max_wall_clock_seconds:
            return "max-wall-clock-seconds"
        if kind in PROVIDER_HEAVY_OPERATION_KINDS and self.counters.llm_calls >= self.profile.max_llm_calls:
            return "max-llm-calls"
        if kind == "pairwiseRanking" and self.counters.pairwise_rounds >= self.profile.max_pairwise_rounds:
            return "max-pairwise-rounds"
        if kind == "directedRevision" and str(operation_id or "").startswith("directed-revision-cycle") and self.counters.revision_cycles >= self.profile.max_revision_cycles:
            return "max-revision-cycles"
        if kind == "directedRevision" and str(operation_id or "").startswith("final-quality-repair-cycle") and self.counters.final_gate_repair_cycles >= self.profile.max_final_gate_repair_cycles:
            return "max-final-gate-repair-cycles"
        if self.counters.consecutive_non_improving_attempts >= self.profile.max_consecutive_non_improving_attempts:
            return "max-consecutive-non-improving-attempts"
        return None

    def _increment(self, kind: str, operation_id: str) -> None:
        if kind in PROVIDER_HEAVY_OPERATION_KINDS:
            self.counters.llm_calls += 1
        if kind == "pairwiseRanking":
            self.counters.pairwise_rounds += 1
        if kind == "directedRevision" and operation_id.startswith("directed-revision-cycle"):
            self.counters.revision_cycles += 1
        if kind == "directedRevision" and operation_id.startswith("final-quality-repair-cycle"):
            self.counters.final_gate_repair_cycles += 1


def normalize_validation_stop_reason(reason: str | None) -> str:
    value = str(reason or "").strip()
    if value in CANONICAL_STOP_REASONS:
        return value
    if value in {"validator-clean", "editorially-improved", "final-quality-gate-passed", "final-quality-repair-accepted"}:
        return STOP_ACCEPTED_QUALITY
    if value in {"max-iterations"}:
        return STOP_MAX_ITERATIONS
    if value in {"no-fresh-angle", "consecutive-non-improving-attempts"}:
        return STOP_NO_IMPROVEMENT
    if value in {"provider-failed", "operation-failed", "provider-unconfigured", "not-run"}:
        return STOP_PROVIDER_INCIDENT
    if value in {"budget-exhausted", "max-wall-clock-seconds", "max-llm-calls", "max-revision-cycles", "max-pairwise-rounds", "max-final-gate-repair-cycles"}:
        return STOP_BUDGET_EXHAUSTED
    if value in {"no-final-candidate", "quality-blocked", "blocked"}:
        return STOP_HUMAN_REVIEW_REQUIRED
    return STOP_HUMAN_REVIEW_REQUIRED if not value else STOP_NO_IMPROVEMENT


def final_validation_stop_reason(
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
        return normalize_validation_stop_reason(loop_stop_reason)
    return normalize_validation_stop_reason(runtime_stop_reason or STOP_HUMAN_REVIEW_REQUIRED)


def finalize_revision_loop_stop(
    guard: ValidationRuntimeGuard | None,
    stop_reason: str,
    detail_stop_reason: str | None,
) -> tuple[str, str | None, dict[str, Any]]:
    canonical = normalize_validation_stop_reason(guard.stop_reason if guard and guard.stop_reason else stop_reason)
    detail = detail_stop_reason
    if canonical != stop_reason:
        detail = detail or stop_reason
    if guard:
        guard.record_stop(canonical, detail=detail)
        return canonical, detail, guard.snapshot()
    return canonical, detail, {}


def operation_denied_by_runtime_budget(
    progress: Any,
    *,
    kind: str,
    operation_id: str,
    detail: str,
) -> bool:
    guard = getattr(progress, "runtime_guard", None) if progress else None
    if guard and not guard.can_start_operation(kind, operation_id):
        guard.record_stop(STOP_BUDGET_EXHAUSTED, detail=detail)
        return True
    return False


def _execution_mode_from_context(context_artifact: Mapping[str, Any] | None) -> str:
    budget = context_artifact.get("draftRunBudget") if isinstance(context_artifact, Mapping) else None
    mode = budget.get("executionMode") if isinstance(budget, Mapping) else None
    try:
        return DraftRunExecutionMode(str(mode or DraftRunExecutionMode.STANDARD.value)).value
    except ValueError:
        return DraftRunExecutionMode.STANDARD.value


def _positive_int(value: int | None) -> int | None:
    if value is None:
        return None
    return max(1, int(value))
