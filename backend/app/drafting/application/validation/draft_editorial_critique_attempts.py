"""Owner: drafting.application.validation

Used by: DraftRun editorial critique service.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.application.json_step_retry_policy import JsonStepAttempt
from backend.app.drafting.application.artifacts.draft_article_memory_service import context_pack_from_payload
from backend.app.domain.ai_run import AiRunProvider
from backend.app.domain.draft_editorial_critique import EditorialCriticAttempt
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.shared.llm_operations import build_operation_envelope, incident_from_safe_error


class EditorialCritiqueAttemptMapper:
    def not_configured_envelope(self, candidate_count: int) -> dict[str, Any]:
        return build_operation_envelope(
            operation_id="editorialCritique",
            operation_kind="reportOnlyValidator",
            owner="backend.app.drafting.application.validation.draft_editorial_critique_service",
            status="notRun",
            attempts=[],
            safe_error="OpenRouter is not configured",
            failure_reason="provider-unconfigured",
            provider=AiRunProvider.OPENROUTER.value,
            input_stats={"candidateCount": candidate_count, "modelRole": DraftModelRole.CRITIC.value},
        )

    def critic_context_pack(self, *payloads: dict[str, Any]) -> dict[str, Any] | None:
        for payload in payloads:
            pack = context_pack_from_payload(payload, DraftModelRole.CRITIC)
            if pack:
                return pack
        return None

    def candidate_report(self, report: dict[str, Any], candidate_id: str) -> dict[str, Any]:
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
        *,
        input_stats: dict[str, Any] | None = None,
        payload_stats: dict[str, Any] | None = None,
    ) -> EditorialCriticAttempt:
        metadata = dict(model_selection)
        if input_stats:
            metadata["inputStats"] = input_stats
        if payload_stats:
            metadata["payloadStats"] = payload_stats
        if validation:
            metadata["incident"] = incident_from_safe_error(
                safe_error=validation,
                probable_cause=status,
                provider=AiRunProvider.OPENROUTER.value,
                model=attempt.model,
                attempt_label=attempt.label,
            ).to_payload()
        return EditorialCriticAttempt(
            label=attempt.label,
            model=attempt.model,
            status=status,
            candidate_id=candidate_id,
            ai_run_id=ai_run_id,
            backup=attempt.backup,
            validation=validation,
            metadata=metadata,
        )

    def candidate_envelope(
        self,
        candidate_id: str,
        attempts: list[EditorialCriticAttempt],
        status: str,
        *,
        payload: dict[str, Any] | None = None,
        safe_error: str | None = None,
        failure_reason: str | None = None,
    ) -> dict[str, Any]:
        return build_operation_envelope(
            operation_id=f"editorialCritique:{candidate_id}",
            operation_kind="reportOnlyValidator",
            owner="backend.app.drafting.application.validation.draft_editorial_critique_service",
            status=status,
            attempts=[attempt.to_payload() for attempt in attempts],
            result_payload=payload or {},
            safe_error=safe_error,
            failure_reason=failure_reason,
            provider=AiRunProvider.OPENROUTER.value,
            model=self.last_attempt_model(attempts),
            input_stats={"candidateCount": 1, "modelRole": DraftModelRole.CRITIC.value, **self.last_input_stats(attempts)},
            payload_stats=self.last_payload_stats(attempts),
        )

    def last_attempt_error(self, attempts: list[EditorialCriticAttempt]) -> str | None:
        return next((attempt.validation for attempt in reversed(attempts) if attempt.validation), None)

    def last_attempt_model(self, attempts: list[EditorialCriticAttempt]) -> str | None:
        return next((str(attempt.model) for attempt in reversed(attempts) if attempt.model), None)

    def last_payload_stats(self, attempts: list[EditorialCriticAttempt]) -> dict[str, Any]:
        return next((dict(attempt.metadata.get("payloadStats")) for attempt in reversed(attempts) if isinstance(attempt.metadata.get("payloadStats"), dict)), {})

    def last_input_stats(self, attempts: list[EditorialCriticAttempt]) -> dict[str, Any]:
        return next((dict(attempt.metadata.get("inputStats")) for attempt in reversed(attempts) if isinstance(attempt.metadata.get("inputStats"), dict)), {})


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
