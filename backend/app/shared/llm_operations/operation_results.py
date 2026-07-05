"""Owner: shared.llm_operations

Used by: Provider-neutral LLM operation result DTOs and result incident policy.
Does not own: Attempt parsing, prompt text, provider adapters, or persistence.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol

from backend.app.shared.llm_operations.attempts import LlmOperationAttempt, attempt_ai_run_ids
from backend.app.shared.llm_operations.incidents import LlmOperationIncident, incident_from_safe_error, redact_safe_error
from backend.app.shared.llm_operations.operation_result_policy import accepted_backup, backup_incident, require_incident
from backend.app.shared.llm_operations.statuses import (
    LlmOperationIncidentSeverity,
    LlmOperationIncidentType,
    LlmOperationResultStatus,
)
from backend.app.shared.llm_operations.stats import LlmOperationRetryPolicy, LlmOperationTimeoutProfile


@dataclass(frozen=True)
class LlmOperationResult:
    operation_id: str
    operation_kind: str
    owner: str
    status: LlmOperationResultStatus
    payload: Mapping[str, Any] = field(default_factory=dict)
    attempts: tuple[LlmOperationAttempt, ...] = ()
    ai_run_ids: tuple[str, ...] = ()
    input_stats: Mapping[str, Any] | None = None
    payload_stats: Mapping[str, Any] | None = None
    retry_policy: LlmOperationRetryPolicy | None = None
    timeout_profile: LlmOperationTimeoutProfile | None = None
    incident: LlmOperationIncident | None = None
    safe_error: str | None = None
    failure_reason: str | None = None
    fallback_used: bool = False

    @classmethod
    def accepted(
        cls,
        *,
        payload: Mapping[str, Any],
        attempts: list[LlmOperationAttempt] | tuple[LlmOperationAttempt, ...],
        operation_id: str = "legacy-json-operation",
        operation_kind: str = "jsonOperation",
        owner: str = "backend.app.drafting.compat",
        input_stats: Mapping[str, Any] | None = None,
        payload_stats: Mapping[str, Any] | None = None,
        retry_policy: LlmOperationRetryPolicy | None = None,
        timeout_profile: LlmOperationTimeoutProfile | None = None,
    ) -> "LlmOperationResult":
        status = LlmOperationResultStatus.BACKUP_ACCEPTED if accepted_backup(attempts) else LlmOperationResultStatus.ACCEPTED
        incident = backup_incident(attempts) if status is LlmOperationResultStatus.BACKUP_ACCEPTED else None
        return cls(
            operation_id=operation_id,
            operation_kind=operation_kind,
            owner=owner,
            status=status,
            payload=dict(payload),
            attempts=tuple(attempts),
            ai_run_ids=attempt_ai_run_ids(attempts),
            input_stats=input_stats,
            payload_stats=payload_stats,
            retry_policy=retry_policy,
            timeout_profile=timeout_profile,
            incident=incident,
        )

    @classmethod
    def fallback(
        cls,
        *,
        payload: Mapping[str, Any],
        attempts: list[LlmOperationAttempt] | tuple[LlmOperationAttempt, ...],
        failure_reason: str | None = None,
        operation_id: str = "legacy-json-operation",
        operation_kind: str = "jsonOperation",
        owner: str = "backend.app.drafting.compat",
        incident: LlmOperationIncident | None = None,
    ) -> "LlmOperationResult":
        incident = incident or LlmOperationIncident(
            incident_type=LlmOperationIncidentType.DETERMINISTIC_FALLBACK,
            incident_severity=LlmOperationIncidentSeverity.WARNING,
            probable_cause=failure_reason or "operation-used-domain-safe-deterministic-fallback",
            needs_follow_up=True,
            safe_error=failure_reason,
        )
        return cls(
            operation_id=operation_id,
            operation_kind=operation_kind,
            owner=owner,
            status=LlmOperationResultStatus.FALLBACK,
            payload=dict(payload),
            attempts=tuple(attempts),
            ai_run_ids=attempt_ai_run_ids(attempts),
            incident=incident,
            safe_error=incident.safe_error,
            failure_reason=failure_reason,
            fallback_used=True,
        )

    @classmethod
    def not_run(
        cls,
        *,
        safe_error: str,
        failure_reason: str,
        attempts: list[LlmOperationAttempt] | tuple[LlmOperationAttempt, ...] = (),
        operation_id: str = "legacy-json-operation",
        operation_kind: str = "jsonOperation",
        owner: str = "backend.app.drafting.compat",
        incident: LlmOperationIncident | None = None,
    ) -> "LlmOperationResult":
        incident = incident or incident_from_safe_error(
            safe_error=safe_error,
            probable_cause=failure_reason,
            incident_type=LlmOperationIncidentType.NOT_CONFIGURED if "configured" in safe_error.lower() else LlmOperationIncidentType.UNKNOWN_PROVIDER_FAILURE,
        )
        return cls(
            operation_id=operation_id,
            operation_kind=operation_kind,
            owner=owner,
            status=LlmOperationResultStatus.NOT_RUN,
            attempts=tuple(attempts),
            ai_run_ids=attempt_ai_run_ids(attempts),
            incident=incident,
            safe_error=safe_error,
            failure_reason=failure_reason,
        )

    @classmethod
    def failed(
        cls,
        *,
        safe_error: str,
        failure_reason: str,
        attempts: list[LlmOperationAttempt] | tuple[LlmOperationAttempt, ...],
        operation_id: str = "legacy-json-operation",
        operation_kind: str = "jsonOperation",
        owner: str = "backend.app.drafting.compat",
        incident: LlmOperationIncident | None = None,
    ) -> "LlmOperationResult":
        incident = incident or incident_from_safe_error(safe_error=safe_error, probable_cause=failure_reason)
        return cls(
            operation_id=operation_id,
            operation_kind=operation_kind,
            owner=owner,
            status=LlmOperationResultStatus.FAILED,
            attempts=tuple(attempts),
            ai_run_ids=attempt_ai_run_ids(attempts),
            incident=incident,
            safe_error=safe_error,
            failure_reason=failure_reason,
        )

    def to_payload(self) -> dict[str, Any]:
        require_incident(self.status, self.incident)
        return {
            "operationId": self.operation_id,
            "operationKind": self.operation_kind,
            "owner": self.owner,
            "status": self.status.value,
            "attempts": [attempt.to_payload() for attempt in self.attempts],
            "aiRunIds": list(self.ai_run_ids),
            "inputStats": dict(self.input_stats or {}),
            "payloadStats": dict(self.payload_stats or {}),
            "retryPolicy": self.retry_policy.to_payload() if self.retry_policy else None,
            "timeoutProfile": self.timeout_profile.to_payload() if self.timeout_profile else None,
            "incident": self.incident.to_payload() if self.incident else None,
            "safeError": redact_safe_error(self.safe_error),
            "failureReason": self.failure_reason,
            "fallbackUsed": self.fallback_used,
            "resultPayload": dict(self.payload),
            "payload": dict(self.payload),
        }


class JsonLlmOperation(Protocol):
    def execute(self, request: Mapping[str, Any]) -> LlmOperationResult:
        ...


JsonOperationResult = LlmOperationResult
JsonOperationEnvelope = LlmOperationResult
LlmOperationEnvelope = LlmOperationResult
