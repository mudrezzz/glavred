from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.deterministic_rhetorical_plan_service import DeterministicRhetoricalPlanService
from backend.app.application.draft_material_plan_service import OpenRouterJsonStepAdapter
from backend.app.application.draft_planning_result import DraftPlanningStepResult
from backend.app.application.draft_rhetorical_plan_audit import (
    build_rhetorical_plan_request_trace,
    build_rhetorical_plan_result_trace,
)
from backend.app.application.draft_rhetorical_plan_prompts import (
    RHETORICAL_PLAN_KEYS,
    RHETORICAL_PLAN_TEMPERATURE,
    build_rhetorical_plan_messages,
)
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_rhetorical_plan import rhetorical_plan_set_from_payload
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings


class DraftRhetoricalPlanService:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        ai_run_service: AiRunService,
        openrouter_validator: OpenRouterConfigValidator,
        openrouter_adapter: OpenRouterJsonStepAdapter,
        deterministic_plan_service: DeterministicRhetoricalPlanService,
    ) -> None:
        self._settings = settings
        self._ai_run_service = ai_run_service
        self._openrouter_validator = openrouter_validator
        self._openrouter_adapter = openrouter_adapter
        self._deterministic_plan_service = deterministic_plan_service

    def create(
        self,
        *,
        context_summary: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        draft_strategy: dict[str, Any],
    ) -> DraftPlanningStepResult:
        post_contract = _record(context_artifact.get("postContract"))
        rule_registry = _record(rule_pack.get("ruleRegistrySnapshot"))
        messages = build_rhetorical_plan_messages(
            context_summary=context_summary,
            rule_registry=rule_registry,
            post_contract=post_contract,
            material_plan=material_plan,
            draft_strategy=draft_strategy,
        )
        status = self._openrouter_validator.evaluate(self._settings)
        provider = AiRunProvider.OPENROUTER if status.configured else AiRunProvider.DETERMINISTIC
        model = self._settings.openrouter_default_model if status.configured else None
        request_payload = build_rhetorical_plan_request_trace(
            provider=provider,
            model=model,
            messages=messages,
            context_summary=context_summary,
            post_contract=post_contract,
            rule_registry=rule_registry,
            material_plan=material_plan,
            draft_strategy=draft_strategy,
        )
        if not status.configured:
            return self._fallback(context_summary, rule_registry, post_contract, material_plan, draft_strategy, request_payload, provider, model, "OpenRouter is not configured")

        try:
            result = self._openrouter_adapter.complete_json(
                settings=self._settings,
                messages=messages,
                expected_keys=RHETORICAL_PLAN_KEYS,
                temperature=RHETORICAL_PLAN_TEMPERATURE,
            )
            plan_set = rhetorical_plan_set_from_payload(result.payload)
            if len(plan_set.plans) < 2:
                raise ValueError("OpenRouter returned fewer than two rhetorical plans")
            payload = plan_set.to_payload()
            run = self._ai_run_service.create_completed_run(
                capability=AiRunCapability.DRAFT_GENERATION,
                provider=AiRunProvider.OPENROUTER,
                model=self._settings.openrouter_default_model,
                request_payload=request_payload,
                result_payload=build_rhetorical_plan_result_trace(
                    result_payload=payload,
                    provider_response=result.raw_response,
                ),
                fallback_used=False,
            )
            return DraftPlanningStepResult(
                artifact_payload=self._artifact("openrouter", payload, run.id, fallback_used=False),
                ai_run_id=run.id,
            )
        except Exception as exc:
            return self._fallback(context_summary, rule_registry, post_contract, material_plan, draft_strategy, request_payload, AiRunProvider.OPENROUTER, model, self._safe_error(exc))

    def _fallback(
        self,
        context_summary: dict[str, Any],
        rule_registry: dict[str, Any],
        post_contract: dict[str, Any],
        material_plan: dict[str, Any],
        draft_strategy: dict[str, Any],
        request_payload: dict[str, Any],
        provider: AiRunProvider,
        model: str | None,
        error: str,
    ) -> DraftPlanningStepResult:
        plan_set = self._deterministic_plan_service.create_plans(
            context_summary=context_summary,
            rule_registry=rule_registry,
            post_contract=post_contract,
            material_plan=material_plan,
            draft_strategy=draft_strategy,
        )
        payload = plan_set.to_payload()
        run = self._ai_run_service.create_completed_run(
            capability=AiRunCapability.DRAFT_GENERATION,
            provider=provider,
            model=model,
            request_payload=request_payload,
            result_payload=build_rhetorical_plan_result_trace(
                result_payload=payload,
                provider_response=None,
                fallback="deterministic",
            ),
            fallback_used=True,
            error=error,
        )
        return DraftPlanningStepResult(
            artifact_payload=self._artifact("deterministicFallback", payload, run.id, fallback_used=True, error=error),
            ai_run_id=run.id,
        )

    def _artifact(
        self,
        source: str,
        payload: dict[str, Any],
        ai_run_id: str,
        *,
        fallback_used: bool,
        error: str | None = None,
    ) -> dict[str, Any]:
        artifact = {"source": source, "aiRunId": ai_run_id, "fallbackUsed": fallback_used, "rhetoricalPlanSet": payload}
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


def _record(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}
