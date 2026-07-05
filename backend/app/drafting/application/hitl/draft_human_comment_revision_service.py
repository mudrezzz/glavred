"""Owner: drafting.application.hitl

Used by: DraftRun hitl package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from dataclasses import dataclass
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.hitl.human_comment_attempt_trace import HumanCommentAttemptTraceBuilder
from backend.app.drafting.application.hitl.human_comment_context import (
    DraftRunLookup,
    HumanCommentTraceContextBuilder,
    HumanCommentVersionCompactor,
)
from backend.app.drafting.application.hitl.human_comment_prompts import HumanCommentRevisionPromptBuilder
from backend.app.drafting.application.hitl.human_comment_revision_attempt_runner import HumanCommentRevisionAttemptRunner
from backend.app.drafting.application.hitl.draft_human_comment_quality_service import DraftHumanCommentQualityService
from backend.app.drafting.application.operations.draft_model_role_resolver import select_model_for_role
from backend.app.application.json_step_retry_policy import build_json_step_attempts
from backend.app.drafting.application.operations.json_step_adapter import DraftingJsonOperationClient
from backend.app.drafting.application.operations.payload_budget_runtime import DraftRunPayloadBudgetRuntime, PayloadBudgetAttemptStatsExtractor
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings


@dataclass(frozen=True)
class HumanCommentRevisionResult:
    title: str
    body: str
    revision_summary: str
    ai_run_id: str | None
    selected_model: str | None
    attempts: list[dict[str, Any]]
    quality_check: dict[str, Any]


class HumanCommentRevisionUnavailable(RuntimeError):
    def __init__(self, message: str, *, attempts: list[dict[str, Any]] | None = None) -> None:
        super().__init__(message)
        self.attempts = attempts or []


class DraftHumanCommentRevisionService:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        ai_run_service: AiRunService,
        openrouter_validator: OpenRouterConfigValidator,
        openrouter_adapter: Any,
        draft_run_repository: DraftRunLookup,
        quality_service: DraftHumanCommentQualityService,
    ) -> None:
        self._settings = settings
        self._ai_run_service = ai_run_service
        self._openrouter_validator = openrouter_validator
        self._openrouter_adapter = openrouter_adapter
        self._draft_run_repository = draft_run_repository
        self._quality_service = quality_service
        self._payload_budget_runtime = DraftRunPayloadBudgetRuntime()
        self._json_client = DraftingJsonOperationClient(openrouter_adapter)
        self._version_compactor = HumanCommentVersionCompactor()
        self._trace_context_builder = HumanCommentTraceContextBuilder(draft_run_repository)
        self._prompt_builder = HumanCommentRevisionPromptBuilder(self._version_compactor)
        self._attempt_stats = PayloadBudgetAttemptStatsExtractor()
        self._trace_builder = HumanCommentAttemptTraceBuilder(
            operation_id="humanCommentRevision",
            operation_kind="hitlWriterRevision",
            owner="backend.app.drafting.application.hitl.draft_human_comment_revision_service",
            model_role=DraftModelRole.WRITER,
        )
        self._attempt_runner = HumanCommentRevisionAttemptRunner(
            settings=settings,
            ai_run_service=ai_run_service,
            json_client=self._json_client,
            payload_budget_runtime=self._payload_budget_runtime,
            version_compactor=self._version_compactor,
            prompt_builder=self._prompt_builder,
            trace_builder=self._trace_builder,
        )

    def revise(
        self,
        *,
        draft_run_id: str | None,
        current_version: dict[str, Any],
        editor_comment: str,
    ) -> HumanCommentRevisionResult:
        comment = editor_comment.strip()
        if not comment:
            raise HumanCommentRevisionUnavailable("Editor comment is required")
        status = self._openrouter_validator.evaluate(self._settings)
        if not status.configured:
            raise HumanCommentRevisionUnavailable(
                "OpenRouter is not configured",
                attempts=[self._trace_builder.not_run_attempt("provider-unconfigured", safe_error="OpenRouter is not configured")],
            )

        trace_context = self._trace_context_builder.build(draft_run_id)
        attempts: list[dict[str, Any]] = []
        repair_context: dict[str, Any] | None = None
        primary_selection = select_model_for_role(self._settings, DraftModelRole.WRITER)
        primary_model = primary_selection.model or self._settings.openrouter_default_model

        for attempt in build_json_step_attempts(
            primary_model=primary_model,
            backup_model=self._settings.openrouter_backup_model_or_none,
        ):
            result = self._attempt_runner.run(
                attempt=attempt,
                primary_selection=primary_selection,
                current_version=current_version,
                editor_comment=comment,
                trace_context=trace_context,
                repair_context=repair_context,
            )
            attempts.append(result["attempt"])
            if result["accepted"]:
                payload = result["payload"]
                revised_version = {
                    "id": current_version.get("id"),
                    "versionNumber": current_version.get("versionNumber"),
                    "title": str(payload.get("title") or "").strip(),
                    "body": str(payload.get("body") or "").strip(),
                }
                quality_check = self._quality_service.check(
                    base_version=current_version,
                    revised_version=revised_version,
                    editor_comment=comment,
                    trace_context=trace_context,
                )
                attempts[-1]["operationEnvelope"] = self._trace_builder.operation_envelope(
                    "accepted",
                    attempts,
                    payload=revised_version,
                    input_stats=self._attempt_stats.last_input_stats(attempts),
                    payload_stats=self._attempt_stats.last_payload_stats(attempts),
                )
                return HumanCommentRevisionResult(
                    title=revised_version["title"],
                    body=revised_version["body"],
                    revision_summary=str(payload.get("revisionSummary") or "").strip(),
                    ai_run_id=result["attempt"].get("aiRunId"),
                    selected_model=result["attempt"].get("selectedModel"),
                    attempts=attempts,
                    quality_check=quality_check.to_payload(),
                )
            repair_context = {
                "previousAttempt": result["attempt"],
                "requiredShape": "title, body, revisionSummary"
            }

        if attempts:
            attempts[-1]["operationEnvelope"] = self._trace_builder.operation_envelope(
                "failed",
                attempts,
                safe_error=self._trace_builder.last_error(attempts),
                failure_reason="human-comment-revision-provider-failed",
                input_stats=self._attempt_stats.last_input_stats(attempts),
                payload_stats=self._attempt_stats.last_payload_stats(attempts),
            )
        raise HumanCommentRevisionUnavailable(
            "Human comment revision failed after all JSON attempts",
            attempts=attempts,
        )
