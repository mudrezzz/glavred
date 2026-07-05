"""Owner: drafting.application.hitl

Used by: DraftRun hitl package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.hitl.human_comment_attempt_trace import HumanCommentAttemptTraceBuilder
from backend.app.drafting.application.hitl.human_comment_context import HumanCommentVersionCompactor
from backend.app.drafting.application.hitl.human_comment_prompts import HumanCommentQualityPromptBuilder
from backend.app.drafting.application.hitl.human_comment_quality_attempt_runner import HUMAN_COMMENT_QUALITY_KEYS, HumanCommentQualityAttemptRunner
from backend.app.drafting.application.hitl.human_comment_quality_components import (
    HumanCommentQualityOverlayPolicy,
    HumanCommentQualityPayloadParser,
)
from backend.app.drafting.application.operations.draft_model_role_resolver import select_model_for_role
from backend.app.application.json_step_retry_policy import build_json_step_attempts
from backend.app.drafting.application.operations.json_step_adapter import DraftingJsonOperationClient
from backend.app.drafting.application.operations.payload_budget_runtime import DraftRunPayloadBudgetRuntime, PayloadBudgetAttemptStatsExtractor
from backend.app.domain.draft_human_revision import HumanCommentRevisionQualityCheck, human_comment_revision_quality_not_run
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings

class DraftHumanCommentQualityService:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        ai_run_service: AiRunService,
        openrouter_validator: OpenRouterConfigValidator,
        openrouter_adapter: Any,
    ) -> None:
        self._settings = settings
        self._ai_run_service = ai_run_service
        self._openrouter_validator = openrouter_validator
        self._openrouter_adapter = openrouter_adapter
        self._payload_budget_runtime = DraftRunPayloadBudgetRuntime()
        self._json_client = DraftingJsonOperationClient(openrouter_adapter)
        self._version_compactor = HumanCommentVersionCompactor()
        self._prompt_builder = HumanCommentQualityPromptBuilder(self._version_compactor)
        self._attempt_stats = PayloadBudgetAttemptStatsExtractor()
        self._payload_parser = HumanCommentQualityPayloadParser()
        self._overlay_policy = HumanCommentQualityOverlayPolicy(self._payload_parser)
        self._trace_builder = HumanCommentAttemptTraceBuilder(
            operation_id="humanCommentRevisionQualityCheck",
            operation_kind="hitlQualityCheck",
            owner="backend.app.drafting.application.hitl.draft_human_comment_quality_service",
            model_role=DraftModelRole.REVIEW,
        )
        self._attempt_runner = HumanCommentQualityAttemptRunner(
            settings=settings,
            ai_run_service=ai_run_service,
            json_client=self._json_client,
            payload_budget_runtime=self._payload_budget_runtime,
            version_compactor=self._version_compactor,
            prompt_builder=self._prompt_builder,
            trace_builder=self._trace_builder,
        )

    def check(
        self,
        *,
        base_version: dict[str, Any],
        revised_version: dict[str, Any],
        editor_comment: str,
        trace_context: dict[str, Any],
    ) -> HumanCommentRevisionQualityCheck:
        status = self._openrouter_validator.evaluate(self._settings)
        if not status.configured:
            return human_comment_revision_quality_not_run(
                reason="OpenRouter is not configured",
                attempts=[self._trace_builder.not_run_attempt("provider-unconfigured", safe_error="OpenRouter is not configured")],
            )

        attempts: list[dict[str, Any]] = []
        repair_context: dict[str, Any] | None = None
        primary_selection = select_model_for_role(self._settings, DraftModelRole.REVIEW)
        primary_model = primary_selection.model or self._settings.openrouter_default_model

        for attempt in build_json_step_attempts(
            primary_model=primary_model,
            backup_model=self._settings.openrouter_backup_model_or_none,
        ):
            result = self._attempt_runner.run(
                attempt=attempt,
                primary_selection=primary_selection,
                base_version=base_version,
                revised_version=revised_version,
                editor_comment=editor_comment,
                trace_context=trace_context,
                repair_context=repair_context,
            )
            attempts.append(result["attempt"])
            if result["accepted"]:
                attempts[-1]["operationEnvelope"] = self._trace_builder.operation_envelope(
                    "accepted",
                    attempts,
                    payload=result["payload"],
                    input_stats=self._attempt_stats.last_input_stats(attempts),
                    payload_stats=self._attempt_stats.last_payload_stats(attempts),
                )
                return self._overlay_policy.apply(
                    self._payload_parser.parse(result["payload"], attempts),
                    base_body=str(base_version.get("body") or ""),
                    revised_body=str(revised_version.get("body") or ""),
                )
            repair_context = {
                "previousAttempt": result["attempt"],
                "requiredShape": ", ".join(sorted(HUMAN_COMMENT_QUALITY_KEYS)),
            }

        if attempts:
            attempts[-1]["operationEnvelope"] = self._trace_builder.operation_envelope(
                "notRun",
                attempts,
                safe_error=self._trace_builder.last_error(attempts),
                failure_reason="human-comment-revision-quality-provider-failed",
                input_stats=self._attempt_stats.last_input_stats(attempts),
                payload_stats=self._attempt_stats.last_payload_stats(attempts),
            )
        return human_comment_revision_quality_not_run(
            reason="Human comment revision quality check failed after all JSON attempts",
            attempts=attempts,
        )
