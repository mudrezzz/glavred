"""Owner: shared.llm_operations

Used by: Provider-neutral LLM operation attempt DTOs and attempt incident mapping.
Does not own: Operation result assembly, prompt text, provider adapters, or persistence.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from backend.app.application.json_step_retry_policy import JsonStepAttempt
from backend.app.shared.llm_operations.incidents import (
    LlmOperationIncident,
    incident_from_payload as _incident_from_payload,
    incident_from_safe_error,
    infer_incident_type as _infer_incident_type,
    redact_safe_error,
)
from backend.app.shared.llm_operations.statuses import (
    LlmOperationAttemptStatus,
    LlmOperationIncidentSeverity,
    LlmOperationIncidentType,
)
from backend.app.shared.llm_operations.stats import _optional_mapping, _optional_str


@dataclass(frozen=True)
class LlmOperationAttempt:
    label: str
    model: str
    status: LlmOperationAttemptStatus = LlmOperationAttemptStatus.PLANNED
    repair: bool = False
    backup: bool = False
    ai_run_id: str | None = None
    error: str | None = None
    validation_reason: str | None = None
    model_role: str | None = None
    selected_model: str | None = None
    model_selection_source: str | None = None
    input_stats: Mapping[str, Any] | None = None
    payload_stats: Mapping[str, Any] | None = None
    generation_params: Mapping[str, Any] | None = None
    incident: LlmOperationIncident | None = None

    @classmethod
    def from_json_step_attempt(
        cls,
        attempt: JsonStepAttempt,
        *,
        status: LlmOperationAttemptStatus = LlmOperationAttemptStatus.PLANNED,
        ai_run_id: str | None = None,
        error: str | None = None,
        validation_reason: str | None = None,
        model_role: str | None = None,
        incident: LlmOperationIncident | None = None,
    ) -> "LlmOperationAttempt":
        return cls(
            label=attempt.label,
            model=attempt.model,
            status=status,
            repair=attempt.repair,
            backup=attempt.backup,
            ai_run_id=ai_run_id,
            error=redact_safe_error(error),
            validation_reason=validation_reason,
            model_role=model_role,
            selected_model=attempt.model,
            incident=incident
            or attempt_incident(
                status=status,
                label=attempt.label,
                model=attempt.model,
                safe_error=error,
                backup=attempt.backup,
            ),
        )

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "LlmOperationAttempt":
        label = str(payload.get("label") or payload.get("attemptLabel") or "unknown")
        error = _optional_str(payload.get("error") or payload.get("validation") or payload.get("safeError"))
        incident_payload = payload.get("incident") if isinstance(payload.get("incident"), Mapping) else None
        status = attempt_status(payload.get("status"))
        selected_model = _optional_str(payload.get("selectedModel") or payload.get("selected_model") or payload.get("model"))
        return cls(
            label=label,
            model=str(payload.get("model") or selected_model or "unknown"),
            status=status,
            repair=bool(payload.get("repair", False) or label.endswith("-repair")),
            backup=bool(payload.get("backup", False)),
            ai_run_id=_optional_str(payload.get("aiRunId") or payload.get("ai_run_id")),
            error=redact_safe_error(error),
            validation_reason=_optional_str(payload.get("validationReason") or payload.get("validation_reason") or payload.get("validation")),
            model_role=_optional_str(payload.get("modelRole") or payload.get("model_role")),
            selected_model=selected_model,
            model_selection_source=_optional_str(payload.get("modelSelectionSource") or payload.get("model_selection_source")),
            input_stats=_optional_mapping(payload.get("inputStats")),
            payload_stats=_optional_mapping(payload.get("payloadStats")),
            generation_params=_optional_mapping(payload.get("generationParams")),
            incident=_incident_from_payload(incident_payload)
            or attempt_incident(status=status, label=label, model=selected_model, safe_error=error, backup=bool(payload.get("backup", False))),
        )

    def to_payload(self) -> dict[str, Any]:
        payload = {
            "label": self.label,
            "model": self.model,
            "status": self.status.value,
            "repair": self.repair,
            "backup": self.backup,
            "aiRunId": self.ai_run_id,
            "error": redact_safe_error(self.error),
            "validationReason": self.validation_reason,
            "modelRole": self.model_role,
            "selectedModel": self.selected_model,
            "modelSelectionSource": self.model_selection_source,
            "inputStats": dict(self.input_stats or {}),
            "payloadStats": dict(self.payload_stats or {}),
            "generationParams": dict(self.generation_params or {}),
        }
        if self.incident:
            payload["incident"] = self.incident.to_payload()
        return payload


def attempt_status(status: Any) -> LlmOperationAttemptStatus:
    normalized = str(status or "planned").replace("-", "").lower()
    aliases = {
        "notrun": LlmOperationAttemptStatus.NOT_RUN,
        "error": LlmOperationAttemptStatus.FAILED,
        "failed": LlmOperationAttemptStatus.FAILED,
        "backupaccepted": LlmOperationAttemptStatus.BACKUP_ACCEPTED,
    }
    if normalized in aliases:
        return aliases[normalized]
    for item in LlmOperationAttemptStatus:
        if item.value.lower() == normalized:
            return item
    return LlmOperationAttemptStatus.PLANNED


def attempt_incident(
    *,
    status: LlmOperationAttemptStatus,
    label: str,
    model: str | None,
    safe_error: str | None,
    backup: bool,
) -> LlmOperationIncident | None:
    if status is LlmOperationAttemptStatus.BACKUP_ACCEPTED or (status is LlmOperationAttemptStatus.ACCEPTED and backup):
        return LlmOperationIncident(
            incident_type=LlmOperationIncidentType.BACKUP_ACCEPTED,
            incident_severity=LlmOperationIncidentSeverity.WARNING,
            probable_cause="primary-attempts-failed-backup-accepted",
            needs_follow_up=True,
            model=model,
            attempt_label=label,
            safe_error=safe_error,
        )
    if status in {
        LlmOperationAttemptStatus.FAILED,
        LlmOperationAttemptStatus.TIMEOUT,
        LlmOperationAttemptStatus.FALLBACK,
        LlmOperationAttemptStatus.NOT_RUN,
    }:
        incident_type = LlmOperationIncidentType.PROVIDER_TIMEOUT if status is LlmOperationAttemptStatus.TIMEOUT else _infer_incident_type(safe_error)
        return incident_from_safe_error(
            safe_error=safe_error or status.value,
            probable_cause=status.value,
            incident_type=incident_type,
            model=model,
            attempt_label=label,
        )
    return None


def attempt_ai_run_ids(attempts: list[LlmOperationAttempt] | tuple[LlmOperationAttempt, ...]) -> tuple[str, ...]:
    values: list[str] = []
    for attempt in attempts:
        if attempt.ai_run_id and attempt.ai_run_id not in values:
            values.append(attempt.ai_run_id)
    return tuple(values)


JsonOperationAttempt = LlmOperationAttempt
