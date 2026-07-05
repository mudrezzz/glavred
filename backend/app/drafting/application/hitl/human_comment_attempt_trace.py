"""Owner: drafting.application.hitl

Used by: Human-comment HITL services for attempt and envelope payloads.
Does not own: Provider execution, prompt construction, persistence, or API response mapping.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.application.json_step_retry_policy import JsonStepAttempt
from backend.app.domain.ai_run import AiRunProvider
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.shared.llm_operations import build_operation_envelope, incident_from_safe_error


class HumanCommentAttemptTraceBuilder:
    def __init__(self, *, operation_id: str, operation_kind: str, owner: str, model_role: DraftModelRole) -> None:
        self._operation_id = operation_id
        self._operation_kind = operation_kind
        self._owner = owner
        self._model_role = model_role

    def attempt_record(
        self,
        attempt: JsonStepAttempt,
        ai_run_id: str,
        status: str,
        model_selection: dict[str, Any],
        validation: str | None = None,
        *,
        input_stats: dict[str, Any] | None = None,
        payload_stats: dict[str, Any] | None = None,
        generation_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        record = {
            "label": attempt.label,
            "model": attempt.model,
            "status": status,
            "aiRunId": ai_run_id,
            "backup": attempt.backup,
            **model_selection,
        }
        if input_stats:
            record["inputStats"] = input_stats
        if payload_stats:
            record["payloadStats"] = payload_stats
        if generation_params:
            record["generationParams"] = generation_params
        if validation:
            record["validation"] = validation
            record["incident"] = incident_from_safe_error(
                safe_error=validation,
                probable_cause=status,
                provider=AiRunProvider.OPENROUTER.value,
                model=attempt.model,
                attempt_label=attempt.label,
            ).to_payload()
        return record

    def not_run_attempt(self, reason: str, *, safe_error: str) -> dict[str, Any]:
        attempt = {
            "label": "not-run",
            "model": "none",
            "status": "notRun",
            "aiRunId": None,
            "backup": False,
            "modelRole": self._model_role.value,
            "selectedModel": None,
            "modelSelectionSource": "unconfigured",
            "incident": incident_from_safe_error(
                safe_error=safe_error,
                probable_cause=reason,
                provider=AiRunProvider.OPENROUTER.value,
                model=None,
                attempt_label="not-run",
            ).to_payload(),
        }
        attempt["operationEnvelope"] = self.operation_envelope(
            "notRun",
            [attempt],
            safe_error=safe_error,
            failure_reason=reason,
        )
        return attempt

    def operation_envelope(
        self,
        status: str,
        attempts: list[dict[str, Any]],
        *,
        payload: dict[str, Any] | None = None,
        safe_error: str | None = None,
        failure_reason: str | None = None,
        input_stats: dict[str, Any] | None = None,
        payload_stats: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return build_operation_envelope(
            operation_id=self._operation_id,
            operation_kind=self._operation_kind,
            owner=self._owner,
            status=status,
            attempts=attempts,
            result_payload=payload or {},
            safe_error=safe_error,
            failure_reason=failure_reason,
            provider=AiRunProvider.OPENROUTER.value,
            model=self.last_model(attempts),
            input_stats={"candidateCount": 1, "modelRole": self._model_role.value, **(input_stats or {})},
            payload_stats=payload_stats,
        )

    def last_error(self, attempts: list[dict[str, Any]]) -> str | None:
        return next((str(item.get("validation")) for item in reversed(attempts) if item.get("validation")), None)

    def last_model(self, attempts: list[dict[str, Any]]) -> str | None:
        return next((str(item.get("model")) for item in reversed(attempts) if item.get("model")), None)
