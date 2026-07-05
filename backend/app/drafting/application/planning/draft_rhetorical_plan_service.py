"""Owner: drafting.application.planning

Used by: DraftRun planning migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.planning.deterministic_rhetorical_plan_service import DeterministicRhetoricalPlanService
from backend.app.drafting.application.operations.json_step_adapter import OpenRouterJsonStepAdapter
from backend.app.drafting.application.planning.draft_planning_result import DraftPlanningStepResult
from backend.app.drafting.application.operations.draft_model_role_resolver import unconfigured_model_selection
from backend.app.drafting.application.artifacts.draft_article_memory_service import context_pack_from_payload
from backend.app.drafting.application.planning.draft_rhetorical_plan_retry import DraftRhetoricalPlanRetryOrchestrator
from backend.app.domain.ai_run import AiRunProvider
from backend.app.domain.draft_model_roles import DraftModelRole
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
        self._openrouter_validator = openrouter_validator
        self._retry = DraftRhetoricalPlanRetryOrchestrator(
            settings=settings,
            ai_run_service=ai_run_service,
            openrouter_adapter=openrouter_adapter,
            deterministic_plan_service=deterministic_plan_service,
        )
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
        context_pack = context_pack_from_payload(context_artifact, DraftModelRole.STRATEGY)
        status = self._openrouter_validator.evaluate(self._settings)
        if status.configured:
            return self._retry.create_with_retry(
                context_summary=context_summary,
                rule_registry=rule_registry,
                post_contract=post_contract,
                material_plan=material_plan,
                draft_strategy=draft_strategy,
                context_pack=context_pack,
            )
        payload = self._deterministic_plan_service.create_plans(
            context_summary=context_summary,
            rule_registry=rule_registry,
            post_contract=post_contract,
            material_plan=material_plan,
            draft_strategy=draft_strategy,
        ).to_payload()
        return DraftPlanningStepResult(
            artifact_payload={
                "source": "deterministicFallback",
                "aiRunId": None,
                "fallbackUsed": True,
                "rhetoricalPlanSet": payload,
                "error": "OpenRouter is not configured",
                "provider": AiRunProvider.DETERMINISTIC.value,
                **unconfigured_model_selection(DraftModelRole.STRATEGY).to_payload(),
            },
            ai_run_id=None,
            ai_run_ids=[],
        )


def _record(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


__all__ = (
    'DraftRhetoricalPlanService',
)
