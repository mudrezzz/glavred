"""Owner: drafting.application.steps

Used by: future DraftRun step implementations and migration adapters.
Does not own: provider adapters, prompt construction, API request parsing, SQLite persistence.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol


class DraftStepOutcomeStatus(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class DraftStepContext:
    run_id: str
    step_key: str
    request_payload: Mapping[str, Any] = field(default_factory=dict)
    prior_artifacts: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "runId": self.run_id,
            "stepKey": self.step_key,
            "requestPayload": dict(self.request_payload),
            "priorArtifacts": {
                key: dict(value) for key, value in self.prior_artifacts.items()
            },
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class DraftStepTrace:
    step_key: str
    operation_name: str | None = None
    ai_run_ids: tuple[str, ...] = ()
    attempts: tuple[Mapping[str, Any], ...] = ()
    warnings: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "stepKey": self.step_key,
            "operationName": self.operation_name,
            "aiRunIds": list(self.ai_run_ids),
            "attempts": [dict(attempt) for attempt in self.attempts],
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class DraftStepOutcome:
    status: DraftStepOutcomeStatus
    artifact_payload: dict[str, Any] = field(default_factory=dict)
    ai_run_ids: tuple[str, ...] = ()
    error: str | None = None
    trace: DraftStepTrace | None = None
    result_payload: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def succeeded(
        cls,
        *,
        artifact_payload: Mapping[str, Any] | None = None,
        ai_run_id: str | None = None,
        ai_run_ids: list[str] | tuple[str, ...] | None = None,
        trace: DraftStepTrace | None = None,
        result_payload: Mapping[str, Any] | None = None,
    ) -> DraftStepOutcome:
        return cls(
            status=DraftStepOutcomeStatus.SUCCEEDED,
            artifact_payload=dict(artifact_payload or {}),
            ai_run_ids=_normalize_ai_run_ids(ai_run_id=ai_run_id, ai_run_ids=ai_run_ids),
            trace=trace,
            result_payload=dict(result_payload or {}),
        )

    @classmethod
    def failed(
        cls,
        *,
        error: str,
        artifact_payload: Mapping[str, Any] | None = None,
        ai_run_ids: list[str] | tuple[str, ...] | None = None,
        trace: DraftStepTrace | None = None,
    ) -> DraftStepOutcome:
        return cls(
            status=DraftStepOutcomeStatus.FAILED,
            artifact_payload=dict(artifact_payload or {}),
            ai_run_ids=_normalize_ai_run_ids(ai_run_ids=ai_run_ids),
            error=error,
            trace=trace,
        )

    @classmethod
    def blocked(
        cls,
        *,
        artifact_payload: Mapping[str, Any] | None = None,
        error: str | None = None,
        trace: DraftStepTrace | None = None,
    ) -> DraftStepOutcome:
        return cls(
            status=DraftStepOutcomeStatus.BLOCKED,
            artifact_payload=dict(artifact_payload or {}),
            error=error,
            trace=trace,
        )

    @classmethod
    def skipped(
        cls,
        *,
        reason: str,
        artifact_payload: Mapping[str, Any] | None = None,
        trace: DraftStepTrace | None = None,
    ) -> DraftStepOutcome:
        return cls(
            status=DraftStepOutcomeStatus.SKIPPED,
            artifact_payload=dict(artifact_payload or {}),
            error=reason,
            trace=trace,
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "artifactPayload": dict(self.artifact_payload),
            "aiRunIds": list(self.ai_run_ids),
            "error": self.error,
            "trace": self.trace.to_payload() if self.trace else None,
            "resultPayload": dict(self.result_payload),
        }


class DraftStep(Protocol):
    def execute(self, context: DraftStepContext) -> DraftStepOutcome:
        ...


def _normalize_ai_run_ids(
    *,
    ai_run_id: str | None = None,
    ai_run_ids: list[str] | tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    normalized: list[str] = []
    for value in [ai_run_id, *(ai_run_ids or [])]:
        if value and value not in normalized:
            normalized.append(value)
    return tuple(normalized)
