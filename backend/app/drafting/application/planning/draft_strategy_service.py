"""Owner: drafting.application.planning

Used by: DraftRun planning migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.planning.deterministic_draft_planning_service import DeterministicDraftPlanningService
from backend.app.drafting.application.operations.json_step_adapter import OpenRouterJsonStepAdapter
from backend.app.drafting.application.operations.draft_model_role_resolver import select_model_for_role, unconfigured_model_selection
from backend.app.drafting.application.planning.draft_planning_audit import (
    PLANNING_TEMPERATURE,
    build_planning_request_trace,
    build_planning_result_trace,
)
from backend.app.drafting.application.planning.draft_planning_prompts import build_draft_strategy_messages
from backend.app.drafting.application.planning.draft_planning_result import DraftPlanningStepResult
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.domain.draft_planning import draft_strategy_from_payload
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings
from backend.app.drafting.application.operations.json_step_adapter import DraftingJsonOperationClient
from backend.app.drafting.application.operations.provider_input_budget_gate import ProviderInputBudgetGate

STRATEGY_KEYS = {
    "thesisAngle",
    "openingMove",
    "argumentSequence",
    "fabulaUsage",
    "ctaPlan",
    "forbiddenMoves",
    "toneNotes",
}


class DraftStrategyService:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        ai_run_service: AiRunService,
        openrouter_validator: OpenRouterConfigValidator,
        openrouter_adapter: OpenRouterJsonStepAdapter,
        deterministic_planning_service: DeterministicDraftPlanningService,
    ) -> None:
        self._settings = settings
        self._ai_run_service = ai_run_service
        self._openrouter_validator = openrouter_validator
        self._openrouter_adapter = openrouter_adapter
        self._deterministic_planning_service = deterministic_planning_service
        self._budget_gate = ProviderInputBudgetGate()

    def create(
        self,
        *,
        context_summary: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        context_pack: dict[str, Any] | None = None,
    ) -> DraftPlanningStepResult:
        status = self._openrouter_validator.evaluate(self._settings)
        provider = AiRunProvider.OPENROUTER if status.configured else AiRunProvider.DETERMINISTIC
        selection = select_model_for_role(self._settings, DraftModelRole.STRATEGY) if status.configured else unconfigured_model_selection(DraftModelRole.STRATEGY)
        model = selection.model
        budget_proof = self._budget_gate.evaluate(
            operation_id="strategy",
            profile_operation_id="draftStrategy",
            draft_run_step="strategy",
            provider_input={
                "context_artifact": {**context_summary, "contextSummary": context_summary, "contextPack": context_pack},
                "rule_pack": rule_pack,
                "material_plan": material_plan,
                "context_pack": context_pack,
            },
            execution_mode=self._settings.draft_run_execution_mode,
            model=model,
            model_role=DraftModelRole.STRATEGY.value,
        )
        prompt_input = budget_proof.budgeted_input.payload
        compact_context = _record(prompt_input.get("context_artifact")).get("contextSummary") or context_summary
        messages = build_draft_strategy_messages(
            context_summary=_record(compact_context),
            rule_pack=_record(prompt_input.get("rule_pack")) or rule_pack,
            material_plan=_record(prompt_input.get("material_plan")) or material_plan,
            context_pack=_record(prompt_input.get("context_pack")) or context_pack,
        )
        request_payload = build_planning_request_trace(
            step="strategy",
            provider=provider,
            model=model,
            messages=messages,
            context_summary=context_summary,
            rule_pack=rule_pack,
            material_plan=material_plan,
            context_pack=context_pack,
            model_selection=selection.to_payload(),
        )
        request_payload.update(budget_proof.request_payload_fields())
        if not status.configured:
            return self._fallback(context_summary, rule_pack, material_plan, request_payload, provider, model, "OpenRouter is not configured")

        try:
            result = DraftingJsonOperationClient(self._openrouter_adapter).complete(
                settings=self._settings,
                messages=messages,
                expected_keys=STRATEGY_KEYS,
                temperature=PLANNING_TEMPERATURE,
                model=model,
            )
            strategy = draft_strategy_from_payload(result.payload)
            payload = strategy.to_payload()
            run = self._ai_run_service.create_completed_run(
                capability=AiRunCapability.DRAFT_GENERATION,
                provider=AiRunProvider.OPENROUTER,
                model=model,
                request_payload=request_payload,
                result_payload=build_planning_result_trace(
                    step="strategy",
                    result_payload=payload,
                    provider_response=result.raw_response,
                ),
                fallback_used=False,
            )
            return DraftPlanningStepResult(
                artifact_payload=self._artifact("openrouter", payload, run.id, selection.to_payload(), fallback_used=False),
                ai_run_id=run.id,
            )
        except Exception as exc:
            return self._fallback(context_summary, rule_pack, material_plan, request_payload, AiRunProvider.OPENROUTER, model, self._safe_error(exc))

    def _fallback(
        self,
        context_summary: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        request_payload: dict[str, Any],
        provider: AiRunProvider,
        model: str | None,
        error: str,
    ) -> DraftPlanningStepResult:
        strategy = self._deterministic_planning_service.create_strategy(
            context_summary=context_summary,
            rule_pack=rule_pack,
            material_plan=material_plan,
        )
        payload = strategy.to_payload()
        run = self._ai_run_service.create_completed_run(
            capability=AiRunCapability.DRAFT_GENERATION,
            provider=provider,
            model=model,
            request_payload=request_payload,
            result_payload=build_planning_result_trace(
                step="strategy",
                result_payload=payload,
                provider_response=None,
                fallback="deterministic",
            ),
            fallback_used=True,
            error=error,
        )
        return DraftPlanningStepResult(
            artifact_payload=self._artifact("deterministicFallback", payload, run.id, {key: request_payload[key] for key in ("modelRole", "selectedModel", "modelSelectionSource") if key in request_payload}, fallback_used=True, error=error),
            ai_run_id=run.id,
        )

    def _artifact(
        self,
        source: str,
        payload: dict[str, Any],
        ai_run_id: str,
        model_selection: dict[str, Any],
        *,
        fallback_used: bool,
        error: str | None = None,
    ) -> dict[str, Any]:
        artifact = {"source": source, "aiRunId": ai_run_id, "fallbackUsed": fallback_used, "draftStrategy": payload}
        artifact.update(model_selection)
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


__all__ = (
    'STRATEGY_KEYS',
    'DraftStrategyService',
)


def _record(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}
