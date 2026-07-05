"""Owner: drafting.application.evidence

Used by: DraftRun evidence migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.evidence.deterministic_source_research_plan_service import DeterministicSourceResearchPlanService
from backend.app.drafting.application.operations.json_step_adapter import OpenRouterJsonStepAdapter
from backend.app.drafting.application.evidence.source_intent_normalizer import SourceIntentNormalizer
from backend.app.drafting.application.evidence.source_research_audit import (
    SOURCE_RESEARCH_TEMPERATURE,
    build_source_research_request_trace,
    build_source_research_result_trace,
)
from backend.app.drafting.application.evidence.source_research_budgeting import apply_source_research_budget
from backend.app.drafting.application.evidence.source_research_plan_sanitizer import sanitize_research_plan_for_source_intent
from backend.app.drafting.application.evidence.source_research_prompts import build_source_research_plan_messages
from backend.app.drafting.application.planning.draft_planning_result import DraftPlanningStepResult
from backend.app.drafting.application.operations.draft_model_role_resolver import select_model_for_role, unconfigured_model_selection
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_generation import DraftGenerationRequest
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.domain.draft_source_intent import research_plan_from_payload
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings
from backend.app.drafting.application.operations.json_step_adapter import DraftingJsonOperationClient

RESEARCH_PLAN_KEYS = {"researchQuestions", "sourceTargets", "verificationTasks", "queryCandidates", "exclusions"}


class SourceResearchPlanService:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        ai_run_service: AiRunService,
        openrouter_validator: OpenRouterConfigValidator,
        openrouter_adapter: OpenRouterJsonStepAdapter,
        normalizer: SourceIntentNormalizer | None = None,
        deterministic_plan_service: DeterministicSourceResearchPlanService | None = None,
    ) -> None:
        self._settings = settings
        self._ai_run_service = ai_run_service
        self._openrouter_validator = openrouter_validator
        self._openrouter_adapter = openrouter_adapter
        self._normalizer = normalizer or SourceIntentNormalizer()
        self._deterministic_plan_service = deterministic_plan_service or DeterministicSourceResearchPlanService()

    def create(self, *, request: DraftGenerationRequest, context_artifact: dict[str, Any]) -> DraftPlanningStepResult:
        source_intent = self._normalizer.normalize(request)
        source_intent_payload = source_intent.to_payload()
        source_origin = _source_origin(context_artifact, request.brief.sources)
        messages = build_source_research_plan_messages(context_artifact=context_artifact, source_intent=source_intent_payload)
        status = self._openrouter_validator.evaluate(self._settings)
        provider = AiRunProvider.OPENROUTER if status.configured else AiRunProvider.DETERMINISTIC
        selection = select_model_for_role(self._settings, DraftModelRole.RESEARCH) if status.configured else unconfigured_model_selection(DraftModelRole.RESEARCH)
        model = selection.model
        request_payload = build_source_research_request_trace(
            provider=provider,
            model=model,
            messages=messages,
            context_artifact=context_artifact,
            source_intent=source_intent_payload,
        )
        request_payload.update(selection.to_payload())
        if not status.configured:
            return self._fallback(source_intent_payload, source_intent, request_payload, provider, model, "OpenRouter is not configured", source_origin, context_artifact)
        try:
            result = DraftingJsonOperationClient(self._openrouter_adapter).complete(
                settings=self._settings,
                messages=messages,
                expected_keys=RESEARCH_PLAN_KEYS,
                temperature=SOURCE_RESEARCH_TEMPERATURE,
                model=model,
            )
            plan_payload = sanitize_research_plan_for_source_intent(
                plan_payload=research_plan_from_payload(result.payload).to_payload(),
                source_intent_payload=source_intent_payload,
            )
            run = self._ai_run_service.create_completed_run(
                capability=AiRunCapability.DRAFT_GENERATION,
                provider=AiRunProvider.OPENROUTER,
                model=model,
                request_payload=request_payload,
                result_payload=build_source_research_result_trace(
                    result_payload=plan_payload,
                    provider_response=result.raw_response,
                ),
                fallback_used=False,
            )
            return DraftPlanningStepResult(
                artifact_payload=apply_source_research_budget(artifact_payload=self._artifact("openrouter", source_origin, source_intent_payload, plan_payload, run.id, selection.to_payload(), fallback_used=False), context_artifact=context_artifact),
                ai_run_id=run.id,
            )
        except Exception as exc:
            return self._fallback(source_intent_payload, source_intent, request_payload, AiRunProvider.OPENROUTER, model, self._safe_error(exc), source_origin, context_artifact)

    def _fallback(
        self,
        source_intent_payload: dict[str, Any],
        source_intent: Any,
        request_payload: dict[str, Any],
        provider: AiRunProvider,
        model: str | None,
        error: str,
        source_origin: str,
        context_artifact: dict[str, Any],
    ) -> DraftPlanningStepResult:
        plan_payload = sanitize_research_plan_for_source_intent(
            plan_payload=self._deterministic_plan_service.create(source_intent).to_payload(),
            source_intent_payload=source_intent_payload,
        )
        run = self._ai_run_service.create_completed_run(
            capability=AiRunCapability.DRAFT_GENERATION,
            provider=provider,
            model=model,
            request_payload=request_payload,
            result_payload=build_source_research_result_trace(
                result_payload=plan_payload,
                provider_response=None,
                fallback="deterministic",
            ),
            fallback_used=True,
            error=error,
        )
        return DraftPlanningStepResult(
            artifact_payload=apply_source_research_budget(artifact_payload=self._artifact("deterministicFallback", source_origin, source_intent_payload, plan_payload, run.id, dict(request_payload), fallback_used=True, error=error), context_artifact=context_artifact),
            ai_run_id=run.id,
        )

    def _artifact(
        self,
        source: str,
        sources_origin: str,
        source_intent: dict[str, Any],
        research_plan: dict[str, Any],
        ai_run_id: str,
        model_selection: dict[str, Any],
        *,
        fallback_used: bool,
        error: str | None = None,
    ) -> dict[str, Any]:
        artifact = {"source": source, "sourcesOrigin": sources_origin, "aiRunId": ai_run_id, "fallbackUsed": fallback_used, "sourceIntent": source_intent, "researchPlan": research_plan}
        artifact.update({key: model_selection[key] for key in ("modelRole", "selectedModel", "modelSelectionSource") if key in model_selection})
        if error:
            artifact["error"] = error
        return artifact

    def _safe_error(self, error: Exception) -> str:
        message = str(error)
        if self._settings.openrouter_api_key:
            token = self._settings.openrouter_api_key.get_secret_value()
            if token:
                message = message.replace(token, "[redacted]")
        return f"{error.__class__.__name__}: {message[:180]}"


def _source_origin(context_artifact: dict[str, Any], sources: list[str]) -> str:
    defaults = context_artifact.get("sourceIntentDefaults")
    if isinstance(defaults, dict) and isinstance(defaults.get("sourcesOrigin"), str):
        return defaults["sourcesOrigin"]
    return "empty" if not sources else "userOverride"


__all__ = (
    'RESEARCH_PLAN_KEYS',
    'SourceResearchPlanService',
)
