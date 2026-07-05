"""Owner: shared.llm_operations

Used by: Provider-heavy operations that need trace-safe operation envelopes.
Does not own: Operation-specific prompts, provider adapters, persistence schemas, or API contracts.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any, Mapping

from backend.app.shared.llm_operations.results import (
    LlmOperationAttempt,
    LlmOperationResult,
    _attempt_ai_run_ids,
    _last_input_stats,
    _result_incident,
    _result_status,
)
from backend.app.shared.llm_operations.statuses import LlmOperationResultStatus
from backend.app.shared.llm_operations.stats import LlmOperationRetryPolicy, LlmOperationTimeoutProfile


class LlmOperationEnvelopeFactory:
    def build(
        self,
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
        envelope_status = _result_status(status, converted_attempts)
        incident = _result_incident(
            status=envelope_status,
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
            status=envelope_status,
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
            fallback_used=envelope_status is LlmOperationResultStatus.FALLBACK,
        )
        return result.to_payload()


build_operation_envelope = LlmOperationEnvelopeFactory().build
