"""Owner: drafting.application.validation

Used by: DraftRun LLM validation service.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.application.json_step_retry_policy import JsonStepAttempt
from backend.app.domain.draft_llm_validation import LlmValidatorAttempt


class LlmValidationAttemptMapper:
    def candidate_deterministic_report(self, report: dict[str, Any], candidate_id: str) -> dict[str, Any]:
        for item in _list(report.get("candidateReports")):
            if isinstance(item, dict) and item.get("candidateId") == candidate_id:
                return item
        return {}

    def attempt(
        self,
        attempt: JsonStepAttempt,
        candidate_id: str,
        status: str,
        ai_run_id: str | None,
        model_selection: dict[str, Any],
        validation: str | None = None,
    ) -> LlmValidatorAttempt:
        return LlmValidatorAttempt(
            label=attempt.label,
            model=attempt.model,
            status=status,
            candidate_id=candidate_id,
            ai_run_id=ai_run_id,
            backup=attempt.backup,
            validation=validation,
            metadata=model_selection,
        )


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
