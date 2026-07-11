"""Owner: drafting.application.generation

Used by: primary and alternative candidate orchestration services.
Does not own: provider execution, prompt construction, AiRun persistence, or fallback.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from typing import Any

from backend.app.application.json_step_retry_policy import JsonStepAttempt


class CandidateAttemptRecordComponent:
    @staticmethod
    def record(attempt: JsonStepAttempt, ai_run_id: str, status: str, model_selection: dict[str, Any], error: str | None = None) -> dict[str, Any]:
        payload = {"label": attempt.label, "model": attempt.model, "status": status, "aiRunId": ai_run_id, "backup": attempt.backup, **model_selection}
        if error:
            payload["validation"] = error
        return payload

    @staticmethod
    def ai_run_ids(attempts: list[dict[str, Any]]) -> list[str]:
        return [str(attempt["aiRunId"]) for attempt in attempts if attempt.get("aiRunId")]

    @staticmethod
    def last_error(attempts: list[dict[str, Any]]) -> str | None:
        return next((str(item.get("validation")) for item in reversed(attempts) if item.get("validation")), None)


__all__ = ("CandidateAttemptRecordComponent",)
