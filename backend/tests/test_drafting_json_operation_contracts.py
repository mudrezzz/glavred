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


def test_json_operation_attempt_converts_existing_retry_attempt() -> None:
    attempt = JsonOperationAttempt.from_json_step_attempt(
        JsonStepAttempt(label="primary-repair", model="openai/gpt-4.1-mini", repair=True),
        status=JsonOperationAttemptStatus.ERROR,
        ai_run_id="ai-repair",
        error="invalid json",
        validation_reason="missing title",
        model_role="writer",
    )

    assert attempt.to_payload() == {
        "label": "primary-repair",
        "model": "openai/gpt-4.1-mini",
        "status": "error",
        "repair": True,
        "backup": False,
        "aiRunId": "ai-repair",
        "error": "invalid json",
        "validationReason": "missing title",
        "modelRole": "writer",
        "selectedModel": "openai/gpt-4.1-mini",
        "modelSelectionSource": None,
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
            status=JsonOperationAttemptStatus.ERROR,
            ai_run_id="ai-primary",
            error="malformed JSON",
        ),
        JsonOperationAttempt.from_json_step_attempt(
            planned[1],
            status=JsonOperationAttemptStatus.ERROR,
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

    assert result.status is JsonOperationResultStatus.ACCEPTED
    assert result.ai_run_ids == ("ai-primary", "ai-repair", "ai-backup")
    assert result.to_payload()["attempts"][2]["backup"] is True
    assert result.to_payload()["payload"] == {"title": "Ok"}


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
    assert not_run.to_payload()["status"] == "not-run"
    assert not_run.to_payload()["safeError"] == "OpenRouter is not configured"
    assert failed.to_payload()["status"] == "failed"
    assert failed.to_payload()["failureReason"] == "operation-failed"
