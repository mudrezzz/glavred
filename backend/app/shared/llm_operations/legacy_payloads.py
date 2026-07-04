"""Owner: shared.llm_operations

Used by: legacy flat provider-heavy services while they migrate to shared envelopes.
Does not own: provider execution, prompt text, retry ordering, or domain-specific fallbacks.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from typing import Any

from backend.app.shared.llm_operations.contracts import build_operation_envelope, incident_from_safe_error


def legacy_operation_envelope(
    status: str,
    attempts: list[dict[str, Any]],
    *,
    operation_id: str,
    operation_kind: str,
    owner: str,
    model_role: str,
    payload: dict[str, Any] | None = None,
    safe_error: str | None = None,
    failure_reason: str | None = None,
    provider: str = "openrouter",
) -> dict[str, Any]:
    return build_operation_envelope(
        operation_id=operation_id,
        operation_kind=operation_kind,
        owner=owner,
        status=status,
        attempts=attempts,
        result_payload=payload or {},
        safe_error=safe_error,
        failure_reason=failure_reason,
        provider=provider,
        model=_last_model(attempts),
        input_stats={"candidateCount": 1, "modelRole": model_role},
    )


def legacy_not_run_result(
    reason: str,
    *,
    operation_id: str,
    operation_kind: str,
    owner: str,
    model_role: str,
    safe_error: str | None = None,
    provider: str = "openrouter",
) -> dict[str, Any]:
    return {
        "status": "not-run",
        "reason": reason,
        "attempts": [],
        "aiRunIds": [],
        "operationEnvelope": legacy_operation_envelope(
            "notRun",
            [],
            operation_id=operation_id,
            operation_kind=operation_kind,
            owner=owner,
            model_role=model_role,
            safe_error=safe_error or reason,
            failure_reason=reason,
            provider=provider,
        ),
    }


def attempt_incident_payload(
    *,
    safe_error: str,
    probable_cause: str,
    provider: str,
    model: str | None,
    attempt_label: str,
) -> dict[str, Any]:
    return incident_from_safe_error(
        safe_error=safe_error,
        probable_cause=probable_cause,
        provider=provider,
        model=model,
        attempt_label=attempt_label,
    ).to_payload()


def legacy_attempt_record(
    attempt: Any,
    ai_run_id: str,
    status: str,
    model_selection: dict[str, Any],
    validation: Any | None = None,
    *,
    provider: str = "openrouter",
) -> dict[str, Any]:
    record = {
        "label": attempt.label,
        "model": attempt.model,
        "status": status,
        "aiRunId": ai_run_id,
        "backup": attempt.backup,
        **model_selection,
    }
    if validation:
        record["validation"] = validation
        record["incident"] = attempt_incident_payload(
            safe_error=str(validation),
            probable_cause=status,
            provider=provider,
            model=attempt.model,
            attempt_label=attempt.label,
        )
    return record


def _last_model(attempts: list[dict[str, Any]]) -> str | None:
    return next((str(item.get("model")) for item in reversed(attempts) if item.get("model")), None)
