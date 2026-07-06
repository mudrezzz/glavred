"""Owner: drafting.application.operations

Used by: DraftRun validation/revision runtime to keep long background loops bounded.
Does not own: Stop-reason vocabulary, provider adapters, prompt text, or persistence.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Callable

from backend.app.drafting.application.operations.validation_runtime_budget_contracts import (
    PROVIDER_HEAVY_OPERATION_KINDS,
    STOP_BUDGET_EXHAUSTED,
    STOP_NO_IMPROVEMENT,
    STOP_PROVIDER_INCIDENT,
    ValidationRuntimeBudgetProfile,
    ValidationRuntimeCounters,
)
from backend.app.drafting.application.operations.validation_runtime_stop_policy import ValidationStopReasonPolicy


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
        return self.denial_reason(kind, operation_id) is None

    def denial_reason(self, kind: str, operation_id: str | None = None) -> str | None:
        return self._denial_reason(kind, operation_id)

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
        canonical = ValidationStopReasonPolicy().normalize(stop_reason)
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
        if (
            kind == "directedRevision"
            and str(operation_id or "").startswith("directed-revision-cycle")
            and self.counters.consecutive_non_improving_attempts >= self.profile.max_consecutive_non_improving_attempts
        ):
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
