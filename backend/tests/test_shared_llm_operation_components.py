from backend.app.application.json_step_retry_policy import JsonStepAttempt
from backend.app.shared.llm_operations import (
    JsonOperationAttempt,
    JsonOperationAttemptStatus,
    JsonOperationResult,
    JsonOperationResultStatus,
    LlmOperationEnvelopeFactory,
    LlmOperationIncident,
    LlmOperationIncidentSeverity,
    LlmOperationIncidentType,
)
from backend.app.shared.llm_operations.incidents import infer_incident_type_value


def test_llm_operation_envelope_factory_preserves_failed_incident_payload() -> None:
    attempt = JsonOperationAttempt.from_json_step_attempt(
        JsonStepAttempt(label="primary", model="model-a"),
        status=JsonOperationAttemptStatus.FAILED,
        ai_run_id="ai-1",
        error="invalid json",
    )

    payload = LlmOperationEnvelopeFactory().build(
        operation_id="op",
        operation_kind="jsonOperation",
        owner="test",
        status="failed",
        attempts=[attempt.to_payload()],
        safe_error="invalid json",
        failure_reason="provider-failed",
    )

    assert payload["operationId"] == "op"
    assert payload["status"] == "failed"
    assert payload["incident"]["incidentType"] == "malformedJson"
    assert payload["attempts"][0]["aiRunId"] == "ai-1"


def test_llm_operation_result_safe_error_redaction_still_applies_after_split() -> None:
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

    assert result.status is JsonOperationResultStatus.FAILED
    assert "sk-test-secret-token" not in payload["safeError"]
    assert "sk-test-secret-token" not in payload["incident"]["safeError"]


def test_incident_classifier_maps_provider_shape_errors_to_schema_failure() -> None:
    assert infer_incident_type_value("OpenRouter response did not include text content") == "schemaFailure"
    assert (
        infer_incident_type_value("availableEvidence does not reference projected source-ledger claims")
        == "schemaFailure"
    )
    assert infer_incident_type_value("OpenRouter response missing keys: weakestMove") == "schemaFailure"
    assert infer_incident_type_value("OpenRouter response JSON parse failed: Expecting ':' delimiter") == "malformedJson"
