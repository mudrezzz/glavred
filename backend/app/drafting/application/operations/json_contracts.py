"""Owner: drafting.application.operations

Used by: DraftRun JSON LLM operation migration adapters and future operation services.
Does not own: provider adapters, prompt text, API request parsing, SQLite persistence.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol

from backend.app.application.json_step_retry_policy import JsonStepAttempt


class JsonOperationAttemptStatus(str, Enum):
    PLANNED = "planned"
    ACCEPTED = "accepted"
    ERROR = "error"
    FALLBACK = "fallback"
    NOT_RUN = "not-run"
    FAILED = "failed"


class JsonOperationResultStatus(str, Enum):
    ACCEPTED = "accepted"
    FALLBACK = "fallback"
    NOT_RUN = "not-run"
    FAILED = "failed"


@dataclass(frozen=True)
class JsonOperationAttempt:
    label: str
    model: str
    status: JsonOperationAttemptStatus = JsonOperationAttemptStatus.PLANNED
    repair: bool = False
    backup: bool = False
    ai_run_id: str | None = None
    error: str | None = None
    validation_reason: str | None = None
    model_role: str | None = None
    selected_model: str | None = None
    model_selection_source: str | None = None

    @classmethod
    def from_json_step_attempt(
        cls,
        attempt: JsonStepAttempt,
        *,
        status: JsonOperationAttemptStatus = JsonOperationAttemptStatus.PLANNED,
        ai_run_id: str | None = None,
        error: str | None = None,
        validation_reason: str | None = None,
        model_role: str | None = None,
    ) -> JsonOperationAttempt:
        return cls(
            label=attempt.label,
            model=attempt.model,
            status=status,
            repair=attempt.repair,
            backup=attempt.backup,
            ai_run_id=ai_run_id,
            error=error,
            validation_reason=validation_reason,
            model_role=model_role,
            selected_model=attempt.model,
        )

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> JsonOperationAttempt:
        status_value = _normalize_status_value(
            payload.get("status"),
            default=JsonOperationAttemptStatus.PLANNED.value,
        )
        label = str(payload.get("label") or payload.get("attemptLabel") or "unknown")
        return cls(
            label=label,
            model=str(payload.get("model") or payload.get("selectedModel") or "unknown"),
            status=JsonOperationAttemptStatus(status_value),
            repair=bool(payload.get("repair", False) or label.endswith("-repair")),
            backup=bool(payload.get("backup", False)),
            ai_run_id=_optional_str(payload.get("aiRunId") or payload.get("ai_run_id")),
            error=_optional_str(payload.get("error")),
            validation_reason=_optional_str(
                payload.get("validationReason") or payload.get("validation_reason")
            ),
            model_role=_optional_str(payload.get("modelRole") or payload.get("model_role")),
            selected_model=_optional_str(payload.get("selectedModel") or payload.get("selected_model")),
            model_selection_source=_optional_str(
                payload.get("modelSelectionSource") or payload.get("model_selection_source")
            ),
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "model": self.model,
            "status": self.status.value,
            "repair": self.repair,
            "backup": self.backup,
            "aiRunId": self.ai_run_id,
            "error": self.error,
            "validationReason": self.validation_reason,
            "modelRole": self.model_role,
            "selectedModel": self.selected_model,
            "modelSelectionSource": self.model_selection_source,
        }


@dataclass(frozen=True)
class JsonOperationResult:
    status: JsonOperationResultStatus
    payload: dict[str, Any] = field(default_factory=dict)
    attempts: tuple[JsonOperationAttempt, ...] = ()
    ai_run_ids: tuple[str, ...] = ()
    safe_error: str | None = None
    failure_reason: str | None = None
    fallback_used: bool = False

    @classmethod
    def accepted(
        cls,
        *,
        payload: Mapping[str, Any],
        attempts: list[JsonOperationAttempt] | tuple[JsonOperationAttempt, ...],
    ) -> JsonOperationResult:
        return cls(
            status=JsonOperationResultStatus.ACCEPTED,
            payload=dict(payload),
            attempts=tuple(attempts),
            ai_run_ids=_attempt_ai_run_ids(attempts),
        )

    @classmethod
    def fallback(
        cls,
        *,
        payload: Mapping[str, Any],
        attempts: list[JsonOperationAttempt] | tuple[JsonOperationAttempt, ...],
        failure_reason: str | None = None,
    ) -> JsonOperationResult:
        return cls(
            status=JsonOperationResultStatus.FALLBACK,
            payload=dict(payload),
            attempts=tuple(attempts),
            ai_run_ids=_attempt_ai_run_ids(attempts),
            failure_reason=failure_reason,
            fallback_used=True,
        )

    @classmethod
    def not_run(
        cls,
        *,
        safe_error: str,
        failure_reason: str,
        attempts: list[JsonOperationAttempt] | tuple[JsonOperationAttempt, ...] = (),
    ) -> JsonOperationResult:
        return cls(
            status=JsonOperationResultStatus.NOT_RUN,
            attempts=tuple(attempts),
            ai_run_ids=_attempt_ai_run_ids(attempts),
            safe_error=safe_error,
            failure_reason=failure_reason,
        )

    @classmethod
    def failed(
        cls,
        *,
        safe_error: str,
        failure_reason: str,
        attempts: list[JsonOperationAttempt] | tuple[JsonOperationAttempt, ...],
    ) -> JsonOperationResult:
        return cls(
            status=JsonOperationResultStatus.FAILED,
            attempts=tuple(attempts),
            ai_run_ids=_attempt_ai_run_ids(attempts),
            safe_error=safe_error,
            failure_reason=failure_reason,
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "payload": dict(self.payload),
            "attempts": [attempt.to_payload() for attempt in self.attempts],
            "aiRunIds": list(self.ai_run_ids),
            "safeError": self.safe_error,
            "failureReason": self.failure_reason,
            "fallbackUsed": self.fallback_used,
        }


class JsonLlmOperation(Protocol):
    def execute(self, request: Mapping[str, Any]) -> JsonOperationResult:
        ...


def _attempt_ai_run_ids(
    attempts: list[JsonOperationAttempt] | tuple[JsonOperationAttempt, ...],
) -> tuple[str, ...]:
    values: list[str] = []
    for attempt in attempts:
        if attempt.ai_run_id and attempt.ai_run_id not in values:
            values.append(attempt.ai_run_id)
    return tuple(values)


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _normalize_status_value(value: Any, *, default: str) -> str:
    if value is None:
        return default
    status = str(value)
    return "not-run" if status == "not_run" else status
