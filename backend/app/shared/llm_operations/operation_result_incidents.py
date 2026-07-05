"""Owner: shared.llm_operations

Used by: LLM operation envelope factory to derive result-level incidents.
Does not own: Attempt DTOs, result DTOs, prompt text, provider adapters, or persistence.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from typing import Any, Mapping

from backend.app.shared.llm_operations.attempts import LlmOperationAttempt
from backend.app.shared.llm_operations.incidents import LlmOperationIncident, incident_from_safe_error
from backend.app.shared.llm_operations.operation_result_policy import backup_incident
from backend.app.shared.llm_operations.statuses import LlmOperationIncidentType, LlmOperationResultStatus


class LlmOperationResultIncidentPolicy:
    def build(
        self,
        *,
        status: LlmOperationResultStatus,
        attempts: tuple[LlmOperationAttempt, ...],
        safe_error: str | None,
        failure_reason: str | None,
        provider: str | None,
        model: str | None,
        payload_stats: Mapping[str, Any] | None,
    ) -> LlmOperationIncident | None:
        if status is LlmOperationResultStatus.BACKUP_ACCEPTED:
            return backup_incident(attempts)
        if status is LlmOperationResultStatus.FALLBACK:
            return incident_from_safe_error(
                safe_error=safe_error or failure_reason or "deterministic fallback used",
                probable_cause=failure_reason or "operation-used-domain-safe-deterministic-fallback",
                incident_type=LlmOperationIncidentType.DETERMINISTIC_FALLBACK,
                provider=provider,
                model=model,
                payload_stats=payload_stats,
            )
        if status is LlmOperationResultStatus.NOT_RUN:
            return incident_from_safe_error(
                safe_error=safe_error or failure_reason or "operation not run",
                probable_cause=failure_reason or "operation-not-run",
                incident_type=LlmOperationIncidentType.NOT_CONFIGURED if self._mentions_not_configured(safe_error, failure_reason) else LlmOperationIncidentType.UNKNOWN_PROVIDER_FAILURE,
                provider=provider,
                model=model,
                payload_stats=payload_stats,
            )
        if status in {
            LlmOperationResultStatus.FAILED,
            LlmOperationResultStatus.TIMEOUT,
            LlmOperationResultStatus.CANCELLED,
            LlmOperationResultStatus.STALE,
        }:
            incident_type = LlmOperationIncidentType.PROVIDER_TIMEOUT if status is LlmOperationResultStatus.TIMEOUT else None
            return incident_from_safe_error(
                safe_error=safe_error or self._last_attempt_error(attempts) or failure_reason or "operation failed",
                probable_cause=failure_reason or "operation-failed",
                incident_type=incident_type,
                provider=provider,
                model=model,
                payload_stats=payload_stats,
            )
        return None

    def _last_attempt_error(self, attempts: tuple[LlmOperationAttempt, ...]) -> str | None:
        return next((attempt.error for attempt in reversed(attempts) if attempt.error), None)

    def _mentions_not_configured(self, *values: str | None) -> bool:
        return any(value and ("not configured" in value.lower() or "unconfigured" in value.lower()) for value in values)


_INCIDENT_POLICY = LlmOperationResultIncidentPolicy()
result_incident = _INCIDENT_POLICY.build
