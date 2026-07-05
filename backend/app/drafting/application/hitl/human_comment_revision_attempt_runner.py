"""Owner: drafting.application.hitl

Used by: Human-comment revision service to run one provider-backed revision attempt.
Does not own: API routing, HITL orchestration loop, quality overlay, or SQLite persistence.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.json_step_retry_policy import JsonStepAttempt
from backend.app.drafting.application.generation.draft_generation_params import GenerationParamProfile, generation_params_for_attempt
from backend.app.drafting.application.hitl.human_comment_attempt_trace import HumanCommentAttemptTraceBuilder
from backend.app.drafting.application.hitl.human_comment_context import HumanCommentVersionCompactor
from backend.app.drafting.application.hitl.human_comment_prompts import HumanCommentRevisionPromptBuilder
from backend.app.drafting.application.operations.draft_model_role_resolver import selection_for_attempt
from backend.app.drafting.application.operations.draft_provider_error_utils import raw_response_excerpt, safe_provider_error
from backend.app.drafting.application.operations.json_step_adapter import DraftingJsonOperationClient
from backend.app.drafting.application.operations.payload_budget_runtime import DraftRunPayloadBudgetRuntime
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.settings import BackendSettings

HUMAN_COMMENT_REVISION_KEYS = {"title", "body", "revisionSummary"}


class HumanCommentRevisionAttemptRunner:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        ai_run_service: AiRunService,
        json_client: DraftingJsonOperationClient,
        payload_budget_runtime: DraftRunPayloadBudgetRuntime,
        version_compactor: HumanCommentVersionCompactor,
        prompt_builder: HumanCommentRevisionPromptBuilder,
        trace_builder: HumanCommentAttemptTraceBuilder,
    ) -> None:
        self._settings = settings
        self._ai_run_service = ai_run_service
        self._json_client = json_client
        self._payload_budget_runtime = payload_budget_runtime
        self._version_compactor = version_compactor
        self._prompt_builder = prompt_builder
        self._trace_builder = trace_builder

    def run(
        self,
        *,
        attempt: JsonStepAttempt,
        primary_selection: Any,
        current_version: dict[str, Any],
        editor_comment: str,
        trace_context: dict[str, Any],
        repair_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        selection = selection_for_attempt(
            role=DraftModelRole.WRITER,
            model=attempt.model,
            backup=attempt.backup,
            primary_selection=primary_selection,
        )
        generation_params = generation_params_for_attempt(
            self._settings,
            primary_profile=GenerationParamProfile.REVISION,
            attempt=attempt,
        )
        attempt_payload = {
            "label": attempt.label,
            "model": attempt.model,
            "repair": attempt.repair,
            "backup": attempt.backup,
            **selection.to_payload(),
        }
        budget_input = self._payload_budget_runtime.compact(
            "humanCommentRevision",
            {
                "current_version": self._version_compactor.compact(current_version),
                "editor_comment": editor_comment,
                "trace_context": trace_context,
            },
            execution_mode=self._settings.draft_run_execution_mode,
            model=attempt.model,
            model_role=DraftModelRole.WRITER.value,
            generation_params=generation_params.to_payload(),
        )
        compact_payload = budget_input.payload
        messages = self._prompt_builder.build_messages(
            current_version=compact_payload["current_version"],
            editor_comment=editor_comment,
            trace_context=compact_payload["trace_context"],
            repair_context=repair_context if attempt.repair else None,
        )
        request_payload = {
            "draftRunStep": "humanCommentRevision",
            "attempt": attempt_payload,
            "currentVersion": self._version_compactor.compact(current_version),
            "editorComment": editor_comment,
            "traceContext": compact_payload["trace_context"],
            "messages": messages,
            "generationParams": generation_params.to_payload(),
            "inputStats": budget_input.input_stats,
            "payloadStats": budget_input.payload_stats,
            "payloadBudget": budget_input.payload_budget,
            **selection.to_payload(),
        }
        try:
            result = self._json_client.complete(
                settings=self._settings,
                messages=messages,
                expected_keys=HUMAN_COMMENT_REVISION_KEYS,
                temperature=generation_params.temperature,
                top_p=generation_params.top_p,
                model=attempt.model,
            )
            title = str(result.payload.get("title") or "").strip()
            body = str(result.payload.get("body") or "").strip()
            if not title or not body:
                raise ValueError("Human comment revision title/body is empty")
            run = self._ai_run_service.create_completed_run(
                capability=AiRunCapability.DRAFT_GENERATION,
                provider=AiRunProvider.OPENROUTER,
                model=attempt.model,
                request_payload=request_payload,
                result_payload={
                    "draftRunStep": "humanCommentRevision",
                    "attempt": attempt_payload,
                    "result": result.payload,
                    "providerResponse": result.raw_response,
                },
                fallback_used=False,
            )
            return {
                "accepted": True,
                "payload": result.payload,
                "attempt": self._trace_builder.attempt_record(
                    attempt,
                    run.id,
                    "accepted",
                    selection.to_payload(),
                    input_stats=budget_input.input_stats,
                    payload_stats=budget_input.payload_stats,
                    generation_params=generation_params.to_payload(),
                ),
            }
        except Exception as exc:
            error = safe_provider_error(self._settings, exc)
            result_payload: dict[str, Any] = {
                "draftRunStep": "humanCommentRevision",
                "attempt": attempt_payload,
                "result": {},
            }
            excerpt = raw_response_excerpt(exc)
            if excerpt:
                result_payload["rawResponseExcerpt"] = excerpt
            run = self._ai_run_service.create_completed_run(
                capability=AiRunCapability.DRAFT_GENERATION,
                provider=AiRunProvider.OPENROUTER,
                model=attempt.model,
                request_payload=request_payload,
                result_payload=result_payload,
                fallback_used=False,
                error=error,
            )
            return {
                "accepted": False,
                "payload": {},
                "attempt": self._trace_builder.attempt_record(
                    attempt,
                    run.id,
                    "error",
                    selection.to_payload(),
                    error,
                    input_stats=request_payload.get("inputStats"),
                    payload_stats=request_payload.get("payloadStats"),
                    generation_params=request_payload.get("generationParams"),
                ),
            }
