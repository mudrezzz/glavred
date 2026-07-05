"""Owner: drafting.application.operations

Used by: Validation runtime budget guard and progress presenters.
Does not own: Provider adapters, prompt text, persistence, or stop-reason decisions.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

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
