"""Owner: shared.llm_operations

Used by: LLM operation result DTOs and envelope factory for result status policy.
Does not own: Result DTO storage, prompt text, provider adapters, or persistence.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from typing import Any

from backend.app.shared.llm_operations.attempts import LlmOperationAttempt
from backend.app.shared.llm_operations.incidents import LlmOperationIncident
from backend.app.shared.llm_operations.statuses import (
    LlmOperationAttemptStatus,
    LlmOperationIncidentSeverity,
    LlmOperationIncidentType,
    LlmOperationResultStatus,
)


class LlmOperationResultPolicy:
    def result_status(self, status: str, attempts: tuple[LlmOperationAttempt, ...]) -> LlmOperationResultStatus:
        normalized = str(status or "").replace("-", "").lower()
        if normalized in {"succeeded", "accepted"}:
            return LlmOperationResultStatus.BACKUP_ACCEPTED if self.accepted_backup(attempts) else LlmOperationResultStatus.ACCEPTED
        if normalized in {"repaired"}:
            return LlmOperationResultStatus.REPAIRED
        if normalized in {"backupaccepted"}:
            return LlmOperationResultStatus.BACKUP_ACCEPTED
        if normalized in {"fallback"}:
            return LlmOperationResultStatus.FALLBACK
        if normalized in {"notrun", "notconfigured"}:
            return LlmOperationResultStatus.NOT_RUN
        if normalized in {"timeout"}:
            return LlmOperationResultStatus.TIMEOUT
        if normalized in {"cancelled"}:
            return LlmOperationResultStatus.CANCELLED
        if normalized in {"stale"}:
            return LlmOperationResultStatus.STALE
        return LlmOperationResultStatus.FAILED

    def require_incident(self, status: LlmOperationResultStatus, incident: LlmOperationIncident | None) -> None:
        if status in {
            LlmOperationResultStatus.FALLBACK,
            LlmOperationResultStatus.NOT_RUN,
            LlmOperationResultStatus.FAILED,
            LlmOperationResultStatus.TIMEOUT,
            LlmOperationResultStatus.CANCELLED,
            LlmOperationResultStatus.STALE,
        } and incident is None:
            raise ValueError(f"{status.value} operation result requires incident metadata")

    def backup_incident(self, attempts: tuple[LlmOperationAttempt, ...] | list[LlmOperationAttempt]) -> LlmOperationIncident:
        backup = next((attempt for attempt in reversed(attempts) if attempt.backup and attempt.status in {LlmOperationAttemptStatus.ACCEPTED, LlmOperationAttemptStatus.BACKUP_ACCEPTED}), None)
        return LlmOperationIncident(
            incident_type=LlmOperationIncidentType.BACKUP_ACCEPTED,
            incident_severity=LlmOperationIncidentSeverity.WARNING,
            probable_cause="primary-attempts-failed-backup-accepted",
            needs_follow_up=True,
            model=backup.model if backup else None,
            attempt_label=backup.label if backup else None,
        )

    def accepted_backup(self, attempts: tuple[LlmOperationAttempt, ...] | list[LlmOperationAttempt]) -> bool:
        return any(attempt.backup and attempt.status in {LlmOperationAttemptStatus.ACCEPTED, LlmOperationAttemptStatus.BACKUP_ACCEPTED} for attempt in attempts)

    def last_input_stats(self, attempts: tuple[LlmOperationAttempt, ...]) -> dict[str, Any]:
        for attempt in reversed(attempts):
            if attempt.input_stats:
                return dict(attempt.input_stats)
        return {}


_RESULT_POLICY = LlmOperationResultPolicy()
result_status = _RESULT_POLICY.result_status
require_incident = _RESULT_POLICY.require_incident
backup_incident = _RESULT_POLICY.backup_incident
accepted_backup = _RESULT_POLICY.accepted_backup
last_input_stats = _RESULT_POLICY.last_input_stats
