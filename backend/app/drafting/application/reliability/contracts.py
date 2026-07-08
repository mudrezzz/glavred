"""Owner: drafting.application.reliability

Used by: DraftRun diagnostics and provider reliability analytics.
Does not own: DraftRun execution, provider transport, retry execution, prompt text, or persistence.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


ReliabilityOutcome = Literal[
    "clean",
    "retryRecovered",
    "backupRecovered",
    "fallbackRecovered",
    "degraded",
    "failed",
    "openCritical",
    "finalGateWarning",
    "payloadTooLarge",
    "contextOverBudget",
]
RemediationDecision = Literal[
    "noActionExpected",
    "watchWithMoreRuns",
    "coveredByExistingSlice",
    "fixBacklogSlice",
    "fixBeforeTrustingQuality",
    "needsManualReview",
]
BlockingLevel = Literal["none", "nextLiveProof", "qualityGate", "productRelease"]
SignalCoverageStatus = Literal["covered", "ignored"]


@dataclass(frozen=True)
class OperationReliabilityEvent:
    """One structured provider or step-quality signal extracted from a DraftRun."""

    run_id: str
    step_key: str
    operation_id: str
    operation_kind: str
    provider: str | None
    model: str | None
    model_role: str | None
    execution_mode: str | None
    attempt_count: int
    retry_path: str
    result_impact: str
    outcome: ReliabilityOutcome
    incident_types: tuple[str, ...]
    source: str

    def group_key(self) -> tuple[str, str, str, str, str, str]:
        return (
            self.operation_id,
            self.step_key,
            self.provider or "unknown",
            self.model or "unknown",
            self.model_role or "unknown",
            self.execution_mode or "unknown",
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "runId": self.run_id,
            "stepKey": self.step_key,
            "operationId": self.operation_id,
            "operationKind": self.operation_kind,
            "provider": self.provider,
            "model": self.model,
            "modelRole": self.model_role,
            "executionMode": self.execution_mode,
            "attemptCount": self.attempt_count,
            "retryPath": self.retry_path,
            "resultImpact": self.result_impact,
            "outcome": self.outcome,
            "incidentTypes": list(self.incident_types),
            "source": self.source,
        }


@dataclass(frozen=True)
class OperationReliabilitySummary:
    """Aggregated reliability counters for one operation/model/execution-mode group."""

    operation_id: str
    step_key: str
    provider: str
    model: str
    model_role: str
    execution_mode: str
    run_ids: tuple[str, ...]
    event_count: int
    outcome_counts: dict[str, int]
    incident_counts: dict[str, int]
    total_attempts: int

    def to_payload(self) -> dict[str, Any]:
        return {
            "operationId": self.operation_id,
            "stepKey": self.step_key,
            "provider": self.provider,
            "model": self.model,
            "modelRole": self.model_role,
            "executionMode": self.execution_mode,
            "runIds": list(self.run_ids),
            "eventCount": self.event_count,
            "outcomeCounts": dict(self.outcome_counts),
            "incidentCounts": dict(self.incident_counts),
            "totalAttempts": self.total_attempts,
        }


@dataclass(frozen=True)
class ProviderReliabilityRemediationItem:
    """A concrete decision for one non-clean reliability signal."""

    decision: RemediationDecision
    operation_id: str
    step_key: str
    provider: str
    model: str
    affected_run_ids: tuple[str, ...]
    evidence_counters: dict[str, int]
    probable_cause: str
    proposed_fix: str
    owner: str
    recommended_slice: str
    blocking_level: BlockingLevel

    def to_payload(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "operationId": self.operation_id,
            "stepKey": self.step_key,
            "provider": self.provider,
            "model": self.model,
            "affectedRunIds": list(self.affected_run_ids),
            "evidenceCounters": dict(self.evidence_counters),
            "probableCause": self.probable_cause,
            "proposedFix": self.proposed_fix,
            "owner": self.owner,
            "recommendedSlice": self.recommended_slice,
            "blockingLevel": self.blocking_level,
        }


@dataclass(frozen=True)
class ReliabilitySignalCoverageRecord:
    """A raw structured signal that the reliability report counted or ignored."""

    run_id: str
    step_key: str
    path: str
    signal_type: str
    coverage_status: SignalCoverageStatus
    reason: str
    operation_id: str | None = None
    incident_type: str | None = None
    ai_run_id: str | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "runId": self.run_id,
            "stepKey": self.step_key,
            "path": self.path,
            "signalType": self.signal_type,
            "coverageStatus": self.coverage_status,
            "reason": self.reason,
            "operationId": self.operation_id,
            "incidentType": self.incident_type,
            "aiRunId": self.ai_run_id,
        }
