"""Owner: shared.llm_operations

Used by: Shared LLM operation incident taxonomy and safe error redaction.
Does not own: Provider adapters, prompt text, persistence schemas, or route responses.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from dataclasses import dataclass
from typing import Any, Mapping

from backend.app.shared.llm_operations.statuses import LlmOperationIncidentSeverity, LlmOperationIncidentType
from backend.app.shared.llm_operations.stats import _optional_mapping, _optional_str

SECRET_MARKERS = ("api_key", "apikey", "authorization", "bearer ", "sk-", "token", "secret")


@dataclass(frozen=True)
class LlmOperationIncident:
    incident_type: LlmOperationIncidentType
    incident_severity: LlmOperationIncidentSeverity
    probable_cause: str
    needs_follow_up: bool
    provider: str | None = None
    model: str | None = None
    attempt_label: str | None = None
    safe_error: str | None = None
    payload_stats: Mapping[str, Any] | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "incidentType": self.incident_type.value,
            "incidentSeverity": self.incident_severity.value,
            "probableCause": self.probable_cause,
            "needsFollowUp": self.needs_follow_up,
            "provider": self.provider,
            "model": self.model,
            "attemptLabel": self.attempt_label,
            "safeError": redact_safe_error(self.safe_error),
            "payloadStats": dict(self.payload_stats or {}),
        }


class LlmOperationIncidentFactory:
    def from_safe_error(
        self,
        *,
        safe_error: str,
        probable_cause: str,
        incident_type: LlmOperationIncidentType | None = None,
        provider: str | None = None,
        model: str | None = None,
        attempt_label: str | None = None,
        payload_stats: Mapping[str, Any] | None = None,
        needs_follow_up: bool = True,
    ) -> LlmOperationIncident:
        inferred_type = incident_type or self.infer_type(safe_error)
        severity = LlmOperationIncidentSeverity.WARNING if inferred_type in {
            LlmOperationIncidentType.BACKUP_ACCEPTED,
            LlmOperationIncidentType.DETERMINISTIC_FALLBACK,
        } else LlmOperationIncidentSeverity.ERROR
        return LlmOperationIncident(
            incident_type=inferred_type,
            incident_severity=severity,
            probable_cause=probable_cause,
            needs_follow_up=needs_follow_up,
            provider=provider,
            model=model,
            attempt_label=attempt_label,
            safe_error=safe_error,
            payload_stats=payload_stats,
        )

    def from_payload(self, payload: Mapping[str, Any] | None) -> LlmOperationIncident | None:
        if not payload:
            return None
        try:
            return LlmOperationIncident(
                incident_type=LlmOperationIncidentType(str(payload.get("incidentType"))),
                incident_severity=LlmOperationIncidentSeverity(str(payload.get("incidentSeverity") or "error")),
                probable_cause=str(payload.get("probableCause") or "unknown"),
                needs_follow_up=bool(payload.get("needsFollowUp", True)),
                provider=_optional_str(payload.get("provider")),
                model=_optional_str(payload.get("model")),
                attempt_label=_optional_str(payload.get("attemptLabel")),
                safe_error=_optional_str(payload.get("safeError")),
                payload_stats=_optional_mapping(payload.get("payloadStats")),
            )
        except ValueError:
            return None

    def infer_type(self, safe_error: str | None) -> LlmOperationIncidentType:
        value = (safe_error or "").lower()
        if "timeout" in value:
            return LlmOperationIncidentType.PROVIDER_TIMEOUT
        if "not configured" in value or "unconfigured" in value:
            return LlmOperationIncidentType.NOT_CONFIGURED
        if "json" in value:
            return LlmOperationIncidentType.MALFORMED_JSON
        if "schema" in value or "validation" in value or "empty" in value or "missing" in value or "not list" in value:
            return LlmOperationIncidentType.SCHEMA_FAILURE
        if " 4" in value or " 400" in value or " 401" in value or " 403" in value:
            return LlmOperationIncidentType.PROVIDER_4XX
        if " 5" in value or " 500" in value or " 502" in value or " 503" in value:
            return LlmOperationIncidentType.PROVIDER_5XX
        if "network" in value or "connection" in value:
            return LlmOperationIncidentType.NETWORK_ERROR
        return LlmOperationIncidentType.UNKNOWN_PROVIDER_FAILURE


class LlmOperationSafeErrorRedactor:
    def redact(self, value: str | None) -> str | None:
        if value is None:
            return None
        result = str(value)[:240]
        lowered = result.lower()
        if any(marker in lowered for marker in SECRET_MARKERS):
            for marker in ("sk-", "Bearer ", "bearer "):
                index = result.find(marker)
                if index >= 0:
                    result = result[:index] + "[redacted]"
            if len(result) > 80 and "[redacted]" not in result:
                result = result[:80] + " [redacted]"
        return result


_INCIDENT_FACTORY = LlmOperationIncidentFactory()
_SAFE_ERROR_REDACTOR = LlmOperationSafeErrorRedactor()
incident_from_safe_error = _INCIDENT_FACTORY.from_safe_error
incident_from_payload = _INCIDENT_FACTORY.from_payload
infer_incident_type = _INCIDENT_FACTORY.infer_type
redact_safe_error = _SAFE_ERROR_REDACTOR.redact
