from typing import Any, Protocol

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.deterministic_draft_planning_service import DeterministicDraftPlanningService
from backend.app.application.draft_planning_result import DraftPlanningStepResult
from backend.app.application.material_plan_evidence_projection import build_usable_evidence_candidates
from backend.app.application.draft_run_budget_resolver import budget_from_context
from backend.app.application.material_plan_retry_orchestrator import MaterialPlanRetryOrchestrator
from backend.app.domain.ai_run import AiRunProvider
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings


class OpenRouterJsonStepAdapter(Protocol):
    def complete_json(
        self,
        *,
        settings: BackendSettings,
        messages: list[dict[str, str]],
        expected_keys: set[str],
        temperature: float,
        top_p: float | None = None,
        model: str | None = None,
    ) -> Any: ...


class DraftMaterialPlanService:
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
        self._openrouter_validator = openrouter_validator
        self._orchestrator = MaterialPlanRetryOrchestrator(
            settings=settings,
            ai_run_service=ai_run_service,
            openrouter_adapter=openrouter_adapter,
            deterministic_planning_service=deterministic_planning_service,
        )

    def create(
        self,
        *,
        context_summary: dict[str, Any],
        rule_pack: dict[str, Any],
        context_artifact: dict[str, Any] | None = None,
    ) -> DraftPlanningStepResult:
        status = self._openrouter_validator.evaluate(self._settings)
        if status.configured:
            return self._orchestrator.create_with_retry(
                context_summary=context_summary,
                rule_pack=rule_pack,
                context_artifact=context_artifact,
            )

        return self._orchestrator.fallback(
            context_summary=context_summary,
            rule_pack=rule_pack,
            usable_candidates=build_usable_evidence_candidates(context_artifact=context_artifact, rule_pack=rule_pack, limit=budget_from_context(context_artifact).caps.max_usable_evidence_candidates),
            attempts=[],
            provider=AiRunProvider.DETERMINISTIC,
            model=None,
            error="OpenRouter is not configured",
        )
