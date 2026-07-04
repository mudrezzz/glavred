from backend.app.application.json_step_retry_policy import (
    JsonStepAttempt,
    build_json_step_attempts,
)
from backend.app.drafting.application.operations.json_contracts import (
    JsonOperationAttempt,
    JsonOperationAttemptStatus,
    JsonOperationResult,
    JsonOperationResultStatus,
)
from backend.app.shared.llm_operations import (
    LlmOperationIncident,
    LlmOperationIncidentSeverity,
    LlmOperationIncidentType,
)


def test_json_operation_attempt_converts_existing_retry_attempt() -> None:
    attempt = JsonOperationAttempt.from_json_step_attempt(
        JsonStepAttempt(label="primary-repair", model="openai/gpt-4.1-mini", repair=True),
        status=JsonOperationAttemptStatus.FAILED,
        ai_run_id="ai-repair",
        error="invalid json",
        validation_reason="missing title",
        model_role="writer",
    )

    assert attempt.to_payload() == {
        "label": "primary-repair",
        "model": "openai/gpt-4.1-mini",
        "status": "failed",
        "repair": True,
        "backup": False,
        "aiRunId": "ai-repair",
        "error": "invalid json",
        "validationReason": "missing title",
        "modelRole": "writer",
        "selectedModel": "openai/gpt-4.1-mini",
        "modelSelectionSource": None,
        "inputStats": {},
        "payloadStats": {},
        "generationParams": {},
        "incident": {
            "incidentType": "malformedJson",
            "incidentSeverity": "error",
            "probableCause": "failed",
            "needsFollowUp": True,
            "provider": None,
            "model": "openai/gpt-4.1-mini",
            "attemptLabel": "primary-repair",
            "safeError": "invalid json",
            "payloadStats": {},
        },
    }


def test_json_operation_attempt_reads_legacy_payload_statuses() -> None:
    attempt = JsonOperationAttempt.from_payload(
        {
            "label": "primary-repair",
            "model": "openai/gpt-4.1-mini",
            "status": "not-run",
            "aiRunId": "ai-1",
            "validationReason": "provider unavailable",
        }
    )

    assert attempt.status is JsonOperationAttemptStatus.NOT_RUN
    assert attempt.repair is True
    assert attempt.ai_run_id == "ai-1"
    assert attempt.validation_reason == "provider unavailable"


def test_json_operation_result_accepts_primary_repair_and_backup_attempts() -> None:
    planned = build_json_step_attempts(
        primary_model="anthropic/claude-sonnet-4.5",
        backup_model="openai/gpt-4.1-mini",
    )
    attempts = [
        JsonOperationAttempt.from_json_step_attempt(
            planned[0],
            status=JsonOperationAttemptStatus.FAILED,
            ai_run_id="ai-primary",
            error="malformed JSON",
        ),
        JsonOperationAttempt.from_json_step_attempt(
            planned[1],
            status=JsonOperationAttemptStatus.FAILED,
            ai_run_id="ai-repair",
            error="still malformed",
        ),
        JsonOperationAttempt.from_json_step_attempt(
            planned[2],
            status=JsonOperationAttemptStatus.ACCEPTED,
            ai_run_id="ai-backup",
        ),
    ]

    result = JsonOperationResult.accepted(payload={"title": "Ok"}, attempts=attempts)

    assert result.status is JsonOperationResultStatus.BACKUP_ACCEPTED
    assert result.ai_run_ids == ("ai-primary", "ai-repair", "ai-backup")
    assert result.to_payload()["attempts"][2]["backup"] is True
    assert result.to_payload()["resultPayload"] == {"title": "Ok"}
    assert result.to_payload()["incident"]["incidentType"] == "backupAccepted"


def test_json_operation_result_fallback_not_run_and_failed_payloads() -> None:
    fallback_attempt = JsonOperationAttempt(
        label="deterministic-fallback",
        model="deterministic",
        status=JsonOperationAttemptStatus.FALLBACK,
        ai_run_id="ai-fallback",
    )

    fallback = JsonOperationResult.fallback(
        payload={"source": "deterministic"},
        attempts=(fallback_attempt,),
        failure_reason="json-attempts-exhausted",
    )
    not_run = JsonOperationResult.not_run(
        safe_error="OpenRouter is not configured",
        failure_reason="provider-unconfigured",
    )
    failed = JsonOperationResult.failed(
        safe_error="provider failed",
        failure_reason="operation-failed",
        attempts=(fallback_attempt,),
    )

    assert fallback.to_payload()["status"] == "fallback"
    assert fallback.to_payload()["fallbackUsed"] is True
    assert fallback.to_payload()["aiRunIds"] == ["ai-fallback"]
    assert not_run.to_payload()["status"] == "notRun"
    assert not_run.to_payload()["safeError"] == "OpenRouter is not configured"
    assert not_run.to_payload()["incident"]["incidentType"] == "notConfigured"
    assert failed.to_payload()["status"] == "failed"
    assert failed.to_payload()["failureReason"] == "operation-failed"


def test_json_operation_result_requires_incident_for_failed_outcomes() -> None:
    result = JsonOperationResult(
        operation_id="manual",
        operation_kind="jsonOperation",
        owner="test",
        status=JsonOperationResultStatus.FAILED,
    )

    try:
        result.to_payload()
    except ValueError as exc:
        assert "requires incident metadata" in str(exc)
    else:
        raise AssertionError("failed result without incident metadata should not serialize")


def test_safe_error_redacts_secret_like_values() -> None:
    result = JsonOperationResult.failed(
        safe_error="provider rejected sk-test-secret-token",
        failure_reason="operation-failed",
        attempts=(),
        incident=LlmOperationIncident(
            incident_type=LlmOperationIncidentType.UNKNOWN_PROVIDER_FAILURE,
            incident_severity=LlmOperationIncidentSeverity.ERROR,
            probable_cause="operation-failed",
            needs_follow_up=True,
            safe_error="provider rejected sk-test-secret-token",
        ),
    )

    payload = result.to_payload()
    assert "sk-test-secret-token" not in payload["safeError"]
    assert "sk-test-secret-token" not in payload["incident"]["safeError"]
