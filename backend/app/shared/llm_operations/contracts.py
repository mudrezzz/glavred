"""Owner: shared.llm_operations

Used by: DraftRun, HITL, future upstream radar/search/signal provider-heavy operations.
Does not own: prompt text, provider adapters, persistence schemas, API response contracts.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol

from backend.app.application.json_step_retry_policy import JsonStepAttempt

SECRET_MARKERS = ("api_key", "apikey", "authorization", "bearer ", "sk-", "token", "secret")


class LlmOperationAttemptStatus(str, Enum):
    PLANNED = "planned"
    ACCEPTED = "accepted"
    REPAIRED = "repaired"
    BACKUP_ACCEPTED = "backupAccepted"
    FALLBACK = "fallback"
    NOT_RUN = "notRun"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    STALE = "stale"


class LlmOperationResultStatus(str, Enum):
    ACCEPTED = "accepted"
    REPAIRED = "repaired"
    BACKUP_ACCEPTED = "backupAccepted"
    FALLBACK = "fallback"
    NOT_RUN = "notRun"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    STALE = "stale"


class LlmOperationIncidentType(str, Enum):
    PROVIDER_TIMEOUT = "providerTimeout"
    NETWORK_ERROR = "networkError"
    PROVIDER_4XX = "provider4xx"
    PROVIDER_5XX = "provider5xx"
    MALFORMED_JSON = "malformedJson"
    SCHEMA_FAILURE = "schemaFailure"
    PAYLOAD_TOO_LARGE = "payloadTooLarge"
    CONTEXT_OVER_BUDGET = "contextOverBudget"
    DETERMINISTIC_FALLBACK = "deterministicFallback"
    BACKUP_ACCEPTED = "backupAccepted"
    NOT_CONFIGURED = "notConfigured"
    STALE_OPERATION = "staleOperation"
    CANCELLED = "cancelled"
    WORKER_FAILURE = "workerFailure"
    UNKNOWN_PROVIDER_FAILURE = "unknownProviderFailure"


class LlmOperationIncidentSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass(frozen=True)
class LlmOperationInputStats:
    prompt_char_estimate: int | None = None
    approx_token_estimate: int | None = None
    rule_count: int | None = None
    evidence_count: int | None = None
    claim_count: int | None = None
    source_count: int | None = None
    candidate_count: int | None = None
    model: str | None = None
    model_role: str | None = None
    generation_params: Mapping[str, Any] | None = None
    extra: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any] | None) -> LlmOperationInputStats:
        source = dict(payload or {})
        return cls(
            prompt_char_estimate=_optional_int(source.pop("promptCharEstimate", None)),
            approx_token_estimate=_optional_int(source.pop("approxTokenEstimate", None)),
            rule_count=_optional_int(source.pop("ruleCount", source.get("compactRuleCount"))),
            evidence_count=_optional_int(source.pop("evidenceCount", None)),
            claim_count=_optional_int(source.pop("claimCount", source.get("externalClaimCount"))),
            source_count=_optional_int(source.pop("sourceCount", None)),
            candidate_count=_optional_int(source.pop("candidateCount", None)),
            model=_optional_str(source.pop("model", source.get("selectedModel"))),
            model_role=_optional_str(source.pop("modelRole", None)),
            generation_params=_optional_mapping(source.pop("generationParams", None)),
            extra={key: value for key, value in source.items() if value is not None},
        )

    def to_payload(self) -> dict[str, Any]:
        payload = {
            "promptCharEstimate": self.prompt_char_estimate,
            "approxTokenEstimate": self.approx_token_estimate,
            "ruleCount": self.rule_count,
            "evidenceCount": self.evidence_count,
            "claimCount": self.claim_count,
            "sourceCount": self.source_count,
            "candidateCount": self.candidate_count,
            "model": self.model,
            "modelRole": self.model_role,
            "generationParams": dict(self.generation_params or {}),
        }
        payload.update(dict(self.extra))
        return payload


@dataclass(frozen=True)
class LlmOperationTimeoutProfile:
    profile: str
    attempt_timeout_seconds: float | None = None
    provider_http_timeout_seconds: float | None = None
    step_budget_seconds: float | None = None
    run_budget_seconds: float | None = None
    stale_watchdog_seconds: float | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "profile": self.profile,
            "attemptTimeoutSeconds": self.attempt_timeout_seconds,
            "providerHttpTimeoutSeconds": self.provider_http_timeout_seconds,
            "stepBudgetSeconds": self.step_budget_seconds,
            "runBudgetSeconds": self.run_budget_seconds,
            "staleWatchdogSeconds": self.stale_watchdog_seconds,
        }


@dataclass(frozen=True)
class LlmOperationRetryPolicy:
    policy: str = "json-primary-repair-backup"
    sequence: tuple[str, ...] = ("primary", "primary-repair", "backup")
    max_attempts: int | None = 3

    def to_payload(self) -> dict[str, Any]:
        return {
            "policy": self.policy,
            "sequence": list(self.sequence),
            "maxAttempts": self.max_attempts,
        }


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
    ) -> LlmOperationAttempt:
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
            or _incident_for_attempt(
                status=status,
                label=attempt.label,
                model=attempt.model,
                safe_error=error,
                backup=attempt.backup,
            ),
        )

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> LlmOperationAttempt:
        label = str(payload.get("label") or payload.get("attemptLabel") or "unknown")
        error = _optional_str(payload.get("error") or payload.get("validation") or payload.get("safeError"))
        incident_payload = payload.get("incident") if isinstance(payload.get("incident"), Mapping) else None
        status = _attempt_status(payload.get("status"))
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
            or _incident_for_attempt(status=status, label=label, model=selected_model, safe_error=error, backup=bool(payload.get("backup", False))),
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
    ) -> LlmOperationResult:
        status = LlmOperationResultStatus.BACKUP_ACCEPTED if _accepted_backup(attempts) else LlmOperationResultStatus.ACCEPTED
        incident = _backup_incident(attempts) if status is LlmOperationResultStatus.BACKUP_ACCEPTED else None
        return cls(
            operation_id=operation_id,
            operation_kind=operation_kind,
            owner=owner,
            status=status,
            payload=dict(payload),
            attempts=tuple(attempts),
            ai_run_ids=_attempt_ai_run_ids(attempts),
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
    ) -> LlmOperationResult:
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
            ai_run_ids=_attempt_ai_run_ids(attempts),
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
    ) -> LlmOperationResult:
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
            ai_run_ids=_attempt_ai_run_ids(attempts),
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
    ) -> LlmOperationResult:
        incident = incident or incident_from_safe_error(safe_error=safe_error, probable_cause=failure_reason)
        return cls(
            operation_id=operation_id,
            operation_kind=operation_kind,
            owner=owner,
            status=LlmOperationResultStatus.FAILED,
            attempts=tuple(attempts),
            ai_run_ids=_attempt_ai_run_ids(attempts),
            incident=incident,
            safe_error=safe_error,
            failure_reason=failure_reason,
        )

    def to_payload(self) -> dict[str, Any]:
        _require_incident(self.status, self.incident)
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


def build_operation_envelope(
    *,
    operation_id: str,
    operation_kind: str,
    owner: str,
    status: str,
    attempts: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...],
    result_payload: Mapping[str, Any] | None = None,
    safe_error: str | None = None,
    failure_reason: str | None = None,
    provider: str | None = None,
    model: str | None = None,
    input_stats: Mapping[str, Any] | None = None,
    payload_stats: Mapping[str, Any] | None = None,
    timeout_profile: LlmOperationTimeoutProfile | None = None,
    retry_policy: LlmOperationRetryPolicy | None = None,
) -> dict[str, Any]:
    converted_attempts = tuple(LlmOperationAttempt.from_payload(attempt) for attempt in attempts)
    result_status = _result_status(status, converted_attempts)
    incident = _result_incident(
        status=result_status,
        attempts=converted_attempts,
        safe_error=safe_error,
        failure_reason=failure_reason,
        provider=provider,
        model=model,
        payload_stats=payload_stats,
    )
    result = LlmOperationResult(
        operation_id=operation_id,
        operation_kind=operation_kind,
        owner=owner,
        status=result_status,
        payload=dict(result_payload or {}),
        attempts=converted_attempts,
        ai_run_ids=_attempt_ai_run_ids(converted_attempts),
        input_stats=input_stats or _last_input_stats(converted_attempts),
        payload_stats=payload_stats,
        retry_policy=retry_policy or LlmOperationRetryPolicy(),
        timeout_profile=timeout_profile,
        incident=incident,
        safe_error=safe_error,
        failure_reason=failure_reason,
        fallback_used=result_status is LlmOperationResultStatus.FALLBACK,
    )
    return result.to_payload()


def incident_from_safe_error(
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
    inferred_type = incident_type or _infer_incident_type(safe_error)
    severity = LlmOperationIncidentSeverity.WARNING if inferred_type in {LlmOperationIncidentType.BACKUP_ACCEPTED, LlmOperationIncidentType.DETERMINISTIC_FALLBACK} else LlmOperationIncidentSeverity.ERROR
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


def redact_safe_error(value: str | None) -> str | None:
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


JsonOperationAttemptStatus = LlmOperationAttemptStatus
JsonOperationResultStatus = LlmOperationResultStatus
JsonOperationAttempt = LlmOperationAttempt
JsonOperationResult = LlmOperationResult
JsonOperationEnvelope = LlmOperationResult
LlmOperationEnvelope = LlmOperationResult


def _result_status(status: str, attempts: tuple[LlmOperationAttempt, ...]) -> LlmOperationResultStatus:
    normalized = str(status or "").replace("-", "").lower()
    if normalized in {"succeeded", "accepted"}:
        return LlmOperationResultStatus.BACKUP_ACCEPTED if _accepted_backup(attempts) else LlmOperationResultStatus.ACCEPTED
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


def _attempt_status(status: Any) -> LlmOperationAttemptStatus:
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


def _result_incident(
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
        return _backup_incident(attempts)
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
            incident_type=LlmOperationIncidentType.NOT_CONFIGURED if _mentions_not_configured(safe_error, failure_reason) else LlmOperationIncidentType.UNKNOWN_PROVIDER_FAILURE,
            provider=provider,
            model=model,
            payload_stats=payload_stats,
        )
    if status in {LlmOperationResultStatus.FAILED, LlmOperationResultStatus.TIMEOUT, LlmOperationResultStatus.CANCELLED, LlmOperationResultStatus.STALE}:
        incident_type = LlmOperationIncidentType.PROVIDER_TIMEOUT if status is LlmOperationResultStatus.TIMEOUT else None
        return incident_from_safe_error(
            safe_error=safe_error or _last_attempt_error(attempts) or failure_reason or "operation failed",
            probable_cause=failure_reason or "operation-failed",
            incident_type=incident_type,
            provider=provider,
            model=model,
            payload_stats=payload_stats,
        )
    return None


def _incident_for_attempt(
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
    if status in {LlmOperationAttemptStatus.FAILED, LlmOperationAttemptStatus.TIMEOUT, LlmOperationAttemptStatus.FALLBACK, LlmOperationAttemptStatus.NOT_RUN}:
        incident_type = LlmOperationIncidentType.PROVIDER_TIMEOUT if status is LlmOperationAttemptStatus.TIMEOUT else _infer_incident_type(safe_error)
        return incident_from_safe_error(
            safe_error=safe_error or status.value,
            probable_cause=status.value,
            incident_type=incident_type,
            model=model,
            attempt_label=label,
        )
    return None


def _incident_from_payload(payload: Mapping[str, Any] | None) -> LlmOperationIncident | None:
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


def _infer_incident_type(safe_error: str | None) -> LlmOperationIncidentType:
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


def _require_incident(status: LlmOperationResultStatus, incident: LlmOperationIncident | None) -> None:
    if status in {
        LlmOperationResultStatus.FALLBACK,
        LlmOperationResultStatus.NOT_RUN,
        LlmOperationResultStatus.FAILED,
        LlmOperationResultStatus.TIMEOUT,
        LlmOperationResultStatus.CANCELLED,
        LlmOperationResultStatus.STALE,
    } and incident is None:
        raise ValueError(f"{status.value} operation result requires incident metadata")


def _backup_incident(attempts: tuple[LlmOperationAttempt, ...] | list[LlmOperationAttempt]) -> LlmOperationIncident:
    backup = next((attempt for attempt in reversed(attempts) if attempt.backup and attempt.status in {LlmOperationAttemptStatus.ACCEPTED, LlmOperationAttemptStatus.BACKUP_ACCEPTED}), None)
    return LlmOperationIncident(
        incident_type=LlmOperationIncidentType.BACKUP_ACCEPTED,
        incident_severity=LlmOperationIncidentSeverity.WARNING,
        probable_cause="primary-attempts-failed-backup-accepted",
        needs_follow_up=True,
        model=backup.model if backup else None,
        attempt_label=backup.label if backup else None,
    )


def _accepted_backup(attempts: tuple[LlmOperationAttempt, ...] | list[LlmOperationAttempt]) -> bool:
    return any(attempt.backup and attempt.status in {LlmOperationAttemptStatus.ACCEPTED, LlmOperationAttemptStatus.BACKUP_ACCEPTED} for attempt in attempts)


def _attempt_ai_run_ids(attempts: list[LlmOperationAttempt] | tuple[LlmOperationAttempt, ...]) -> tuple[str, ...]:
    values: list[str] = []
    for attempt in attempts:
        if attempt.ai_run_id and attempt.ai_run_id not in values:
            values.append(attempt.ai_run_id)
    return tuple(values)


def _last_input_stats(attempts: tuple[LlmOperationAttempt, ...]) -> dict[str, Any]:
    for attempt in reversed(attempts):
        if attempt.input_stats:
            return dict(attempt.input_stats)
    return {}


def _last_attempt_error(attempts: tuple[LlmOperationAttempt, ...]) -> str | None:
    return next((attempt.error for attempt in reversed(attempts) if attempt.error), None)


def _mentions_not_configured(*values: str | None) -> bool:
    return any(value and ("not configured" in value.lower() or "unconfigured" in value.lower()) for value in values)


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_mapping(value: Any) -> Mapping[str, Any] | None:
    return value if isinstance(value, Mapping) else None
