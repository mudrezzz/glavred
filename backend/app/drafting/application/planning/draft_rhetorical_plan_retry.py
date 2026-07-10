"""Owner: drafting.application.planning

Used by: DraftRun rhetorical-plan generation.
Does not own: prompt construction, provider transport, attempt recording, or API routing.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.json_step_retry_policy import build_json_step_attempts
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.drafting.application.operations.draft_model_role_resolver import select_model_for_role
from backend.app.drafting.application.operations.provider_input_budget_gate import ProviderInputBudgetGate
from backend.app.drafting.application.planning.deterministic_rhetorical_plan_service import (
    DeterministicRhetoricalPlanService,
)
from backend.app.drafting.application.planning.draft_planning_result import DraftPlanningStepResult
from backend.app.drafting.application.planning.draft_rhetorical_plan_attempt_component import (
    RhetoricalPlanAttemptComponent,
)
from backend.app.drafting.application.planning.draft_rhetorical_plan_audit import (
    build_rhetorical_plan_request_trace,
    build_rhetorical_plan_result_trace,
)
from backend.app.drafting.domain.provider_dossier import DossierReadinessStatus, ProviderDossier
from backend.app.settings import BackendSettings


class DraftRhetoricalPlanRetryOrchestrator:
    """Chooses attempts and falls back after all provider attempts fail."""

    def __init__(
        self,
        *,
        settings: BackendSettings,
        ai_run_service: AiRunService,
        openrouter_adapter: Any,
        deterministic_plan_service: DeterministicRhetoricalPlanService,
    ) -> None:
        self._settings = settings
        self._ai_run_service = ai_run_service
        self._deterministic_plan_service = deterministic_plan_service
        self._attempt_component = RhetoricalPlanAttemptComponent(
            settings=settings,
            ai_run_service=ai_run_service,
            openrouter_adapter=openrouter_adapter,
        )
        self._budget_gate = ProviderInputBudgetGate()

    def create_with_retry(
        self,
        *,
        context_summary: dict[str, Any],
        rule_registry: dict[str, Any],
        post_contract: dict[str, Any],
        material_plan: dict[str, Any],
        draft_strategy: dict[str, Any],
        provider_dossier: ProviderDossier,
        context_pack: dict[str, Any] | None = None,
    ) -> DraftPlanningStepResult:
        attempts: list[dict[str, Any]] = []
        if provider_dossier.readiness_status == DossierReadinessStatus.BLOCKED:
            return self._fallback(
                context_summary=context_summary,
                rule_registry=rule_registry,
                post_contract=post_contract,
                material_plan=material_plan,
                draft_strategy=draft_strategy,
                attempts=attempts,
                provider_dossier=provider_dossier,
                context_pack=context_pack,
                error=(
                    "Planning dossier blocked: "
                    + ", ".join(provider_dossier.missing_required_inputs)
                ),
            )
        repair_context: dict[str, Any] | None = None
        primary_selection = select_model_for_role(self._settings, DraftModelRole.STRATEGY)
        for attempt in build_json_step_attempts(
            primary_model=primary_selection.model or self._settings.openrouter_default_model,
            backup_model=self._settings.openrouter_backup_model_or_none,
        ):
            result = self._attempt_component.execute(
                attempt=attempt,
                primary_selection=primary_selection,
                context_summary=context_summary,
                rule_registry=rule_registry,
                post_contract=post_contract,
                material_plan=material_plan,
                draft_strategy=draft_strategy,
                provider_dossier=provider_dossier,
                context_pack=context_pack,
                repair_context=repair_context,
            )
            attempts.append(result["attempt"])
            if result["accepted"]:
                return DraftPlanningStepResult(
                    artifact_payload=self._artifact(
                        "openrouter",
                        result["payload"],
                        result["aiRunId"],
                        False,
                        attempts=attempts,
                    ),
                    ai_run_id=result["aiRunId"],
                    ai_run_ids=[
                        str(item["aiRunId"])
                        for item in attempts
                        if item.get("aiRunId")
                    ],
                )
            repair_context = {
                "previousAttempt": result["attempt"],
                "requiredShape": "object with plans[2..3]",
            }
        return self._fallback(
            context_summary=context_summary,
            rule_registry=rule_registry,
            post_contract=post_contract,
            material_plan=material_plan,
            draft_strategy=draft_strategy,
            attempts=attempts,
            provider_dossier=provider_dossier,
            context_pack=context_pack,
        )

    def _fallback(
        self,
        *,
        context_summary: dict[str, Any],
        rule_registry: dict[str, Any],
        post_contract: dict[str, Any],
        material_plan: dict[str, Any],
        draft_strategy: dict[str, Any],
        attempts: list[dict[str, Any]],
        provider_dossier: ProviderDossier,
        context_pack: dict[str, Any] | None = None,
        error: str = "RhetoricalPlans JSON generation failed after all LLM attempts",
    ) -> DraftPlanningStepResult:
        payload = self._deterministic_plan_service.create_plans(
            context_summary=context_summary,
            rule_registry=rule_registry,
            post_contract=post_contract,
            material_plan=material_plan,
            draft_strategy=draft_strategy,
        ).to_payload()
        budget_proof = self._budget_gate.evaluate(
            operation_id="rhetoricalPlans",
            draft_run_step="rhetoricalPlans",
            provider_input=provider_dossier.provider_input(),
            execution_mode=self._settings.draft_run_execution_mode,
            model=self._settings.openrouter_default_model,
            model_role=DraftModelRole.STRATEGY.value,
        )
        request_payload = build_rhetorical_plan_request_trace(
            provider=AiRunProvider.OPENROUTER,
            model=self._settings.openrouter_default_model,
            messages=[],
            context_summary=context_summary,
            post_contract=post_contract,
            rule_registry=rule_registry,
            material_plan=material_plan,
            draft_strategy=draft_strategy,
            context_pack=context_pack,
            provider_dossier=provider_dossier.to_payload(),
        )
        request_payload.update(budget_proof.request_payload_fields())
        run = self._ai_run_service.create_completed_run(
            capability=AiRunCapability.DRAFT_GENERATION,
            provider=AiRunProvider.OPENROUTER,
            model=self._settings.openrouter_default_model,
            request_payload={
                **request_payload,
                "attempts": attempts,
                "modelRole": DraftModelRole.STRATEGY.value,
            },
            result_payload=build_rhetorical_plan_result_trace(
                result_payload=payload,
                provider_response=None,
                fallback="deterministic",
            ),
            fallback_used=True,
            error=error,
        )
        fallback_attempt = {
            "label": "deterministic-fallback",
            "model": "deterministic",
            "status": "fallback",
            "aiRunId": run.id,
            "backup": False,
            "modelRole": DraftModelRole.STRATEGY.value,
            "modelSelectionSource": "unconfigured",
            "selectedModel": None,
        }
        return DraftPlanningStepResult(
            artifact_payload=self._artifact(
                "deterministicFallback",
                payload,
                run.id,
                True,
                error=error,
                attempts=[*attempts, fallback_attempt],
            ),
            ai_run_id=run.id,
            ai_run_ids=[
                str(item["aiRunId"])
                for item in attempts
                if item.get("aiRunId")
            ]
            + [run.id],
        )

    @staticmethod
    def _artifact(
        source: str,
        payload: dict[str, Any],
        ai_run_id: str,
        fallback_used: bool,
        *,
        attempts: list[dict[str, Any]],
        error: str | None = None,
    ) -> dict[str, Any]:
        artifact = {
            "source": source,
            "aiRunId": ai_run_id,
            "fallbackUsed": fallback_used,
            "rhetoricalPlanSet": payload,
            "attempts": attempts,
        }
        if error:
            artifact["error"] = error
        return artifact


__all__ = ("DraftRhetoricalPlanRetryOrchestrator",)
