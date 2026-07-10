"""Owner: drafting.application.planning

Used by: rhetorical-plan retry orchestration.
Does not own: retry ordering, deterministic fallback, API routing, or persistence policy.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.json_step_retry_policy import JsonStepAttempt
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.domain.draft_rhetorical_plan import rhetorical_plan_set_from_payload
from backend.app.drafting.application.operations.draft_model_role_resolver import selection_for_attempt
from backend.app.drafting.application.operations.json_step_adapter import DraftingJsonOperationClient
from backend.app.drafting.application.operations.provider_input_budget_gate import ProviderInputBudgetGate
from backend.app.drafting.application.planning.draft_rhetorical_plan_audit import (
    build_rhetorical_plan_request_trace,
    build_rhetorical_plan_result_trace,
)
from backend.app.drafting.application.planning.draft_rhetorical_plan_prompts import (
    RHETORICAL_PLAN_KEYS,
    RHETORICAL_PLAN_TEMPERATURE,
    build_rhetorical_plan_messages,
)
from backend.app.drafting.domain.provider_dossier import ProviderDossier
from backend.app.settings import BackendSettings


class RhetoricalPlanAttemptComponent:
    """Builds, budgets, executes, and records one rhetorical-plan attempt."""

    def __init__(
        self,
        *,
        settings: BackendSettings,
        ai_run_service: AiRunService,
        openrouter_adapter: Any,
    ) -> None:
        self._settings = settings
        self._ai_run_service = ai_run_service
        self._operation_client = DraftingJsonOperationClient(openrouter_adapter)
        self._budget_gate = ProviderInputBudgetGate()

    def execute(
        self,
        *,
        attempt: JsonStepAttempt,
        primary_selection: Any,
        context_summary: dict[str, Any],
        rule_registry: dict[str, Any],
        post_contract: dict[str, Any],
        material_plan: dict[str, Any],
        draft_strategy: dict[str, Any],
        provider_dossier: ProviderDossier,
        context_pack: dict[str, Any] | None,
        repair_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        selection = selection_for_attempt(
            role=DraftModelRole.STRATEGY,
            model=attempt.model,
            backup=attempt.backup,
            primary_selection=primary_selection,
        )
        attempt_payload = {
            "label": attempt.label,
            "model": attempt.model,
            "repair": attempt.repair,
            "backup": attempt.backup,
            **selection.to_payload(),
        }
        provider_input = provider_dossier.provider_input()
        if attempt.repair and repair_context:
            provider_input = {**provider_input, "repairContext": repair_context}
        budget_proof = self._budget_gate.evaluate(
            operation_id="rhetoricalPlans",
            draft_run_step="rhetoricalPlans",
            provider_input=provider_input,
            execution_mode=self._settings.draft_run_execution_mode,
            model=attempt.model,
            model_role=DraftModelRole.STRATEGY.value,
        )
        messages = build_rhetorical_plan_messages(
            dossier_input=budget_proof.budgeted_input.payload,
        )
        request_payload = build_rhetorical_plan_request_trace(
            provider=AiRunProvider.OPENROUTER,
            model=attempt.model,
            messages=messages,
            context_summary=context_summary,
            post_contract=post_contract,
            rule_registry=rule_registry,
            material_plan=material_plan,
            draft_strategy=draft_strategy,
            context_pack=context_pack,
            attempt=attempt_payload,
            model_selection=selection.to_payload(),
            provider_dossier=provider_dossier.to_payload(),
        )
        request_payload.update(budget_proof.request_payload_fields())
        try:
            result = self._operation_client.complete(
                settings=self._settings,
                messages=messages,
                expected_keys=RHETORICAL_PLAN_KEYS,
                temperature=RHETORICAL_PLAN_TEMPERATURE,
                model=attempt.model,
            )
            payload = rhetorical_plan_set_from_payload(result.payload).to_payload()
            if len(payload.get("plans") or []) < 2:
                raise ValueError("OpenRouter returned fewer than two rhetorical plans")
            run = self._ai_run_service.create_completed_run(
                capability=AiRunCapability.DRAFT_GENERATION,
                provider=AiRunProvider.OPENROUTER,
                model=attempt.model,
                request_payload=request_payload,
                result_payload=build_rhetorical_plan_result_trace(
                    result_payload=payload,
                    provider_response=result.raw_response,
                    attempt=attempt_payload,
                ),
                fallback_used=False,
            )
            return {
                "accepted": True,
                "payload": payload,
                "aiRunId": run.id,
                "attempt": self.attempt_record(
                    attempt,
                    run.id,
                    "accepted",
                    selection.to_payload(),
                ),
            }
        except Exception as exc:
            return self._record_error(attempt, request_payload, self._safe_error(exc))

    def attempt_record(
        self,
        attempt: JsonStepAttempt,
        ai_run_id: str,
        status: str,
        model_selection: dict[str, Any],
        validation: Any | None = None,
    ) -> dict[str, Any]:
        record = {
            "label": attempt.label,
            "model": attempt.model,
            "status": status,
            "aiRunId": ai_run_id,
            "backup": attempt.backup,
            **model_selection,
        }
        if validation:
            record["validation"] = validation
        return record

    def _record_error(
        self,
        attempt: JsonStepAttempt,
        request_payload: dict[str, Any],
        error: str,
    ) -> dict[str, Any]:
        run = self._ai_run_service.create_completed_run(
            capability=AiRunCapability.DRAFT_GENERATION,
            provider=AiRunProvider.OPENROUTER,
            model=attempt.model,
            request_payload=request_payload,
            result_payload=build_rhetorical_plan_result_trace(
                result_payload={"plans": []},
                provider_response=None,
                attempt=request_payload.get("attempt"),
            ),
            fallback_used=False,
            error=error,
        )
        model_selection = {
            key: request_payload[key]
            for key in ("modelRole", "selectedModel", "modelSelectionSource")
            if key in request_payload
        }
        return {
            "accepted": False,
            "payload": {},
            "aiRunId": run.id,
            "attempt": self.attempt_record(
                attempt,
                run.id,
                "error",
                model_selection,
                error,
            ),
        }

    def _safe_error(self, error: Exception) -> str:
        message = str(error)
        if self._settings.openrouter_api_key:
            token = self._settings.openrouter_api_key.get_secret_value()
            if token:
                message = message.replace(token, "[redacted]")
        return f"{error.__class__.__name__}: {message[:180]}"


__all__ = ("RhetoricalPlanAttemptComponent",)
