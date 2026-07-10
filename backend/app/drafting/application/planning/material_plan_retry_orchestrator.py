"""Owner: drafting.application.planning

Used by: DraftRun planning migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.planning.deterministic_draft_planning_service import DeterministicDraftPlanningService
from backend.app.drafting.application.planning.draft_planning_audit import (
    PLANNING_TEMPERATURE,
    build_planning_request_trace,
    build_planning_result_trace,
)
from backend.app.drafting.application.planning.draft_planning_prompts import build_material_plan_messages
from backend.app.drafting.application.planning.draft_planning_result import DraftPlanningStepResult
from backend.app.drafting.application.operations.draft_model_role_resolver import select_model_for_role, selection_for_attempt, unconfigured_model_selection
from backend.app.drafting.application.artifacts.draft_context_pack_builder import context_pack_for_role
from backend.app.drafting.application.planning.material_plan_accountability import evaluate_material_plan_accountability
from backend.app.drafting.application.planning.material_plan_evidence_projection import (
    build_dossier_evidence_candidates,
    build_usable_evidence_candidates,
)
from backend.app.drafting.application.artifacts.draft_run_budget_resolver import budget_from_context
from backend.app.drafting.application.planning.material_plan_retry_policy import (
    MaterialPlanAttempt,
    build_material_plan_attempts,
    compact_material_plan_repair_context,
)
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.domain.draft_planning import material_plan_from_payload
from backend.app.settings import BackendSettings
from backend.app.drafting.application.operations.json_step_adapter import DraftingJsonOperationClient
from backend.app.drafting.application.operations.provider_input_budget_gate import ProviderInputBudgetGate
from backend.app.drafting.domain.provider_dossier import DossierReadinessStatus, ProviderDossier

MATERIAL_PLAN_KEYS = {
    "availableEvidence",
    "rejectedEvidence",
    "rejectionReasons",
    "claimsRequiringAttribution",
    "qualifiedClaims",
    "missingEvidence",
    "riskyClaims",
    "groundingPlan",
    "sourceNotes",
    "openQuestions",
}


class MaterialPlanRetryOrchestrator:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        ai_run_service: AiRunService,
        openrouter_adapter: Any,
        deterministic_planning_service: DeterministicDraftPlanningService,
    ) -> None:
        self._settings = settings
        self._ai_run_service = ai_run_service
        self._openrouter_adapter = openrouter_adapter
        self._deterministic_planning_service = deterministic_planning_service
        self._budget_gate = ProviderInputBudgetGate()

    def create_with_retry(
        self,
        *,
        context_summary: dict[str, Any],
        rule_pack: dict[str, Any],
        provider_dossier: ProviderDossier,
        context_artifact: dict[str, Any] | None,
    ) -> DraftPlanningStepResult:
        budget = budget_from_context(context_artifact)
        rich_candidates = build_usable_evidence_candidates(
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            limit=budget.caps.max_usable_evidence_candidates,
        )
        dossier_candidates = build_dossier_evidence_candidates(
            provider_dossier,
            limit=budget.caps.max_usable_evidence_candidates,
        )
        usable_candidates = rich_candidates or dossier_candidates
        context_pack = context_pack_for_role(context_artifact, DraftModelRole.STRATEGY)
        if provider_dossier.readiness_status == DossierReadinessStatus.BLOCKED:
            return self.fallback(
                context_summary=context_summary,
                rule_pack=rule_pack,
                provider_dossier=provider_dossier,
                usable_candidates=usable_candidates,
                context_pack=context_pack,
                attempts=[],
                provider=AiRunProvider.DETERMINISTIC,
                model=None,
                error=f"Planning dossier blocked: {', '.join(provider_dossier.missing_required_inputs)}",
            )
        attempt_records: list[dict[str, Any]] = []
        repair_context: dict[str, Any] | None = None
        primary_selection = select_model_for_role(self._settings, DraftModelRole.STRATEGY)
        for attempt in build_material_plan_attempts(
            primary_model=primary_selection.model or self._settings.openrouter_default_model,
            backup_model=self._settings.openrouter_backup_model_or_none,
        ):
            result = self._try_attempt(
                attempt=attempt,
                primary_selection=primary_selection,
                context_summary=context_summary,
                rule_pack=rule_pack,
                provider_dossier=provider_dossier,
                usable_candidates=usable_candidates,
                context_pack=context_pack,
                repair_context=repair_context,
            )
            attempt_records.append(result["attempt"])
            if result["accepted"]:
                return DraftPlanningStepResult(
                    artifact_payload=self._artifact(
                        "openrouter",
                        result["payload"],
                        result["aiRunId"],
                        fallback_used=False,
                        attempts=attempt_records,
                        usable_evidence_candidates=usable_candidates,
                        accountability=result["accountability"],
                    ),
                    ai_run_id=result["aiRunId"],
                    ai_run_ids=[str(item["aiRunId"]) for item in attempt_records if item.get("aiRunId")],
                )
            repair_context = compact_material_plan_repair_context(
                result["attempt"],
                result["accountability"].get("invalidReasons", []),
            )

        return self.fallback(
            context_summary=context_summary,
            rule_pack=rule_pack,
            provider_dossier=provider_dossier,
            usable_candidates=usable_candidates,
            context_pack=context_pack,
            attempts=attempt_records,
            provider=AiRunProvider.OPENROUTER,
            model=primary_selection.model,
            error="MaterialPlan evidence accountability failed after all LLM attempts",
        )

    def fallback(
        self,
        *,
        context_summary: dict[str, Any],
        rule_pack: dict[str, Any],
        provider_dossier: ProviderDossier,
        usable_candidates: list[dict[str, Any]],
        attempts: list[dict[str, Any]],
        provider: AiRunProvider,
        model: str | None,
        error: str,
        context_pack: dict[str, Any] | None = None,
    ) -> DraftPlanningStepResult:
        selection = unconfigured_model_selection(DraftModelRole.STRATEGY) if model is None else select_model_for_role(self._settings, DraftModelRole.STRATEGY)
        payload = self._deterministic_planning_service.create_material_plan(
            context_summary=context_summary,
            rule_pack=rule_pack,
        ).to_payload()
        accountability = evaluate_material_plan_accountability(
            material_plan_payload=payload,
            usable_evidence_candidates=usable_candidates,
        ).to_payload()
        budget_proof = self._budget_gate.evaluate(
            operation_id="materialPlan",
            draft_run_step="materialPlan",
            provider_input=provider_dossier.provider_input(),
            execution_mode=self._settings.draft_run_execution_mode,
            model=model,
            model_role=DraftModelRole.STRATEGY.value,
        )
        request_payload = build_planning_request_trace(
            step="materialPlan",
            provider=provider,
            model=model,
            messages=[],
            context_summary=context_summary,
            rule_pack=rule_pack,
            usable_evidence_candidates=usable_candidates,
            context_pack=context_pack,
            attempt={"label": "emergency-fallback", "model": model, "repair": False, "backup": False},
            model_selection=selection.to_payload(),
            provider_dossier=provider_dossier.to_payload(),
        )
        request_payload.update(budget_proof.request_payload_fields())
        run = self._ai_run_service.create_completed_run(
            capability=AiRunCapability.DRAFT_GENERATION,
            provider=provider,
            model=model,
            request_payload=request_payload,
            result_payload=build_planning_result_trace(
                step="materialPlan",
                result_payload={
                    **payload,
                    "evidenceAccountability": accountability,
                    "usableEvidenceCandidates": usable_candidates,
                    "attempts": attempts,
                },
                provider_response=None,
                fallback="deterministicEmergency",
            ),
            fallback_used=True,
            error=error,
        )
        fallback_attempt = {
            "label": "emergency-fallback",
            "model": model or "deterministic",
            "status": "fallback",
            "aiRunId": run.id,
            "backup": False,
            "validation": accountability,
            **selection.to_payload(),
        }
        return DraftPlanningStepResult(
            artifact_payload=self._artifact(
                "deterministicFallback",
                payload,
                run.id,
                fallback_used=True,
                error=error,
                attempts=[*attempts, fallback_attempt],
                usable_evidence_candidates=usable_candidates,
                accountability=accountability,
            ),
            ai_run_id=run.id,
            ai_run_ids=[str(item["aiRunId"]) for item in attempts if item.get("aiRunId")] + [run.id],
        )

    def _try_attempt(
        self,
        *,
        attempt: MaterialPlanAttempt,
        primary_selection: Any,
        context_summary: dict[str, Any],
        rule_pack: dict[str, Any],
        provider_dossier: ProviderDossier,
        usable_candidates: list[dict[str, Any]],
        context_pack: dict[str, Any] | None,
        repair_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        budget_proof = self._budget_gate.evaluate(
            operation_id="materialPlan",
            draft_run_step="materialPlan",
            provider_input={
                **provider_dossier.provider_input(),
                **({"repairContext": repair_context} if attempt.repair and repair_context else {}),
            },
            execution_mode=self._settings.draft_run_execution_mode,
            model=attempt.model,
            model_role=DraftModelRole.STRATEGY.value,
        )
        prompt_input = budget_proof.budgeted_input.payload
        messages = build_material_plan_messages(
            dossier_input=prompt_input,
        )
        request_payload = build_planning_request_trace(
            step="materialPlan",
            provider=AiRunProvider.OPENROUTER,
            model=attempt.model,
            messages=messages,
            context_summary=context_summary,
            rule_pack=rule_pack,
            usable_evidence_candidates=usable_candidates,
            context_pack=context_pack,
            attempt={"label": attempt.label, "model": attempt.model, "repair": attempt.repair, "backup": attempt.backup},
            model_selection=selection_for_attempt(role=DraftModelRole.STRATEGY, model=attempt.model, backup=attempt.backup, primary_selection=primary_selection).to_payload(),
            provider_dossier=provider_dossier.to_payload(),
        )
        request_payload.update(budget_proof.request_payload_fields())
        try:
            return self._record_provider_attempt(attempt, request_payload, messages, usable_candidates)
        except Exception as exc:
            return self._record_attempt_error(attempt, request_payload, self._safe_error(exc))

    def _record_provider_attempt(
        self,
        attempt: MaterialPlanAttempt,
        request_payload: dict[str, Any],
        messages: list[dict[str, str]],
        usable_candidates: list[dict[str, Any]],
    ) -> dict[str, Any]:
        result = DraftingJsonOperationClient(self._openrouter_adapter).complete(
            settings=self._settings,
            messages=messages,
            expected_keys=MATERIAL_PLAN_KEYS,
            temperature=PLANNING_TEMPERATURE,
            model=attempt.model,
        )
        payload = material_plan_from_payload(result.payload).to_payload()
        accountability = evaluate_material_plan_accountability(
            material_plan_payload=payload,
            usable_evidence_candidates=usable_candidates,
        )
        run = self._ai_run_service.create_completed_run(
            capability=AiRunCapability.DRAFT_GENERATION,
            provider=AiRunProvider.OPENROUTER,
            model=attempt.model,
            request_payload=request_payload,
            result_payload=build_planning_result_trace(
                step="materialPlan",
                result_payload={**payload, "evidenceAccountability": accountability.to_payload(), "attempt": attempt.__dict__},
                provider_response=result.raw_response,
            ),
            fallback_used=False,
            error=None if accountability.valid else "; ".join(accountability.invalid_reasons),
        )
        return {
            "accepted": accountability.valid,
            "payload": payload,
            "aiRunId": run.id,
            "accountability": accountability.to_payload(),
            "attempt": self._attempt_record(attempt, run.id, "accepted" if accountability.valid else "rejected", accountability.to_payload()),
        }

    def _record_attempt_error(self, attempt: MaterialPlanAttempt, request_payload: dict[str, Any], error: str) -> dict[str, Any]:
        accountability = {"valid": False, "invalidReasons": [error]}
        run = self._ai_run_service.create_completed_run(
            capability=AiRunCapability.DRAFT_GENERATION,
            provider=AiRunProvider.OPENROUTER,
            model=attempt.model,
            request_payload=request_payload,
            result_payload=build_planning_result_trace(
                step="materialPlan",
                result_payload={"attempt": attempt.__dict__, "evidenceAccountability": accountability},
                provider_response=None,
            ),
            fallback_used=False,
            error=error,
        )
        return {
            "accepted": False,
            "payload": {},
            "aiRunId": run.id,
            "accountability": accountability,
            "attempt": self._attempt_record(attempt, run.id, "error", accountability),
        }

    def _attempt_record(self, attempt: MaterialPlanAttempt, ai_run_id: str, status: str, validation: dict[str, Any]) -> dict[str, Any]:
        source = "backup" if attempt.backup else ("role" if self._settings.draft_strategy_model.strip() else "default")
        return {
            "label": attempt.label,
            "model": attempt.model,
            "status": status,
            "aiRunId": ai_run_id,
            "backup": attempt.backup,
            "validation": validation,
            "modelRole": DraftModelRole.STRATEGY.value,
            "modelSelectionSource": source,
            "selectedModel": attempt.model,
        }

    def _artifact(
        self,
        source: str,
        payload: dict[str, Any],
        ai_run_id: str,
        *,
        fallback_used: bool,
        error: str | None = None,
        attempts: list[dict[str, Any]] | None = None,
        usable_evidence_candidates: list[dict[str, Any]] | None = None,
        accountability: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        artifact = {"source": source, "aiRunId": ai_run_id, "fallbackUsed": fallback_used, "materialPlan": payload}
        if attempts is not None:
            artifact["attempts"] = attempts
        if usable_evidence_candidates is not None:
            artifact["usableEvidenceCandidates"] = usable_evidence_candidates
        if accountability is not None:
            artifact["evidenceAccountability"] = accountability
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
    'MATERIAL_PLAN_KEYS',
    'MaterialPlanRetryOrchestrator',
)
