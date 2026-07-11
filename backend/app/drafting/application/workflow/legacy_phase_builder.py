"""Owner: drafting.application.workflow

Used by: legacy DraftRun workflow factory during behavior-preserving migration.
Does not own: provider adapters, prompt text, API request parsing, SQLite persistence.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

import json
from typing import Any

from backend.app.drafting.application.artifacts.draft_context_pack_builder import context_pack_for_role
from backend.app.drafting.application.generation.draft_candidate_selection_block import candidate_selection_blocked_payload
from backend.app.drafting.application.artifacts.draft_run_context_builder import build_draft_run_context_summary
from backend.app.drafting.application.artifacts.draft_run_context_payloads import context_from_payload
from backend.app.drafting.application.artifacts.draft_run_payloads import draft_to_payload, payload_section
from backend.app.drafting.application.artifacts.draft_run_budget_resolver import resolve_draft_run_budget
from backend.app.drafting.application.quality import DraftRunQualityFidelityReporter
from backend.app.drafting.application.context.draft_run_context_access import DraftRunContextAccessService
from backend.app.drafting.application.dossiers.provider_dossier_factories import PlanningDossierFactory, WriterDossierFactory
from backend.app.application.draft_run_step_progress_payload import with_progress_payload
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.domain.draft_run import DraftRunStatus
from backend.app.domain.draft_run_steps import DraftRunStepKey
from backend.app.drafting.domain.provider_dossier import ProviderDossier
from backend.app.drafting.application.operations.validation_runtime_budget import (
    ValidationRuntimeBudgetPolicy,
    ValidationRuntimeGuard,
)
from backend.app.drafting.application.operations.provider_input_budget_gate import ProviderInputBudgetGate
from backend.app.drafting.application.workflow.legacy_services import LegacyDraftWorkflowServices
from backend.app.drafting.application.workflow.registry import DraftStepRegistry, DraftWorkflowPhase
from backend.app.drafting.application.workflow.state import DraftWorkflowState
from backend.app.settings import get_settings


class LegacyDraftWorkflowPhaseBuilder:
    def __init__(self, services: LegacyDraftWorkflowServices) -> None:
        self._services = services
        self._quality_fidelity = DraftRunQualityFidelityReporter()

    def build_registry(self) -> DraftStepRegistry:
        return DraftStepRegistry(
            [
                DraftWorkflowPhase("context", (DraftRunStepKey.CONTEXT,), self.context),
                DraftWorkflowPhase("source-intent", (DraftRunStepKey.SOURCE_INTENT,), self.source_intent),
                DraftWorkflowPhase("public-evidence", (DraftRunStepKey.PUBLIC_EVIDENCE,), self.public_evidence),
                DraftWorkflowPhase(
                    "feasibility-contract",
                    (DraftRunStepKey.FEASIBILITY, DraftRunStepKey.POST_CONTRACT),
                    self.feasibility_contract,
                ),
                DraftWorkflowPhase("rule-pack", (DraftRunStepKey.RULE_PACK,), self.rule_pack),
                DraftWorkflowPhase("material-plan", (DraftRunStepKey.MATERIAL_PLAN,), self.material_plan),
                DraftWorkflowPhase("strategy", (DraftRunStepKey.STRATEGY,), self.strategy),
                DraftWorkflowPhase(
                    "rhetorical-plans",
                    (DraftRunStepKey.RHETORICAL_PLANS,),
                    self.rhetorical_plans_phase,
                ),
                DraftWorkflowPhase("draft", (DraftRunStepKey.DRAFT,), self.draft),
                DraftWorkflowPhase("validation", (DraftRunStepKey.VALIDATION,), self.validation),
                DraftWorkflowPhase("complete", (DraftRunStepKey.COMPLETE,), self.complete),
            ]
        )

    def context(self, state: DraftWorkflowState) -> None:
        state.context_summary = build_draft_run_context_summary(
            state.request,
            context_from_payload(state.run.request_payload),
        )
        source_ledger = self._services.source_ledger_builder.build(
            state.context_summary,
            state.request,
        ).to_payload()
        state.context_artifact = {
            **state.context_summary,
            "sourceLedger": source_ledger,
            "draftRunBudget": resolve_draft_run_budget(
                {**state.context_summary, "sourceLedger": source_ledger}
            ).to_payload(),
        }
        state.context_summary = {
            **state.context_summary,
            "draftRunBudget": state.context_artifact["draftRunBudget"],
        }
        state.progress.complete(DraftRunStepKey.CONTEXT, state.context_artifact)

    def source_intent(self, state: DraftWorkflowState) -> None:
        state.source_result = self._services.source_research_plan_service.create(
            request=state.request,
            context_artifact=state.context_artifact,
        )
        state.progress.add_ai_run_id(state.source_result.ai_run_id)
        state.context_artifact = {
            **state.context_artifact,
            **state.source_result.artifact_payload,
        }
        state.progress.complete(
            DraftRunStepKey.SOURCE_INTENT,
            state.source_result.artifact_payload,
        )

    def public_evidence(self, state: DraftWorkflowState) -> None:
        state.progress.start(DraftRunStepKey.PUBLIC_EVIDENCE)
        public_progress = state.progress.operation_sink(DraftRunStepKey.PUBLIC_EVIDENCE)
        result = self._services.public_evidence_step_service.run(
            source_intent_artifact=state.source_result.artifact_payload,
            context_artifact=state.context_artifact,
            progress=public_progress,
        )
        state.progress.add_ai_run_ids(result.ai_run_ids)
        state.context_artifact = self._services.article_memory.attach(
            result.context_artifact,
            context_artifact=result.context_artifact,
        )
        state.progress.succeed(
            DraftRunStepKey.PUBLIC_EVIDENCE,
            with_progress_payload(
                self._services.article_memory.attach(
                    result.artifact_payload,
                    context_artifact=state.context_artifact,
                ),
                public_progress,
            ),
        )

    def feasibility_contract(self, state: DraftWorkflowState) -> None:
        result = self._services.quality_gate.evaluate(state.context_artifact)
        state.progress.complete(DraftRunStepKey.FEASIBILITY, result.feasibility_report)
        state.progress.complete(DraftRunStepKey.POST_CONTRACT, result.post_contract)
        if result.blocked:
            quality_fidelity = self._quality_fidelity.build_from_run(
                self._services.repository.get(state.run_id),
                final_draft=None,
            )
            state.progress.complete(
                DraftRunStepKey.COMPLETE,
                {**(result.complete_payload or {"status": "blocked"}), "qualityFidelity": quality_fidelity},
            )
            self._services.repository.set_run_status(
                state.run_id,
                DraftRunStatus.SUCCEEDED,
                ai_run_ids=[],
            )
            state.stop("feasibility-blocked")
            return
        state.context_artifact = result.context_artifact

    def rule_pack(self, state: DraftWorkflowState) -> None:
        state.progress.start(DraftRunStepKey.RULE_PACK)
        rule_progress = state.progress.operation_sink(DraftRunStepKey.RULE_PACK)
        state.rule_pack = self._services.rule_pack_compiler.compile(
            state.context_artifact
        ).to_payload()
        interpretation = self._services.evidence_interpretation_service.create(
            context_summary=state.context_summary,
            context_artifact=state.context_artifact,
            rule_pack=state.rule_pack,
            context_pack=context_pack_for_role(state.context_artifact, DraftModelRole.STRATEGY),
            progress=rule_progress,
        )
        state.progress.add_ai_run_ids(
            interpretation.ai_run_ids
            or ([interpretation.ai_run_id] if interpretation.ai_run_id else [])
        )
        state.rule_pack = {**state.rule_pack, **interpretation.artifact_payload}
        state.context_artifact = {**state.context_artifact, **interpretation.artifact_payload}
        artifact = self._services.article_memory.attach(
            state.rule_pack,
            context_artifact=state.context_artifact,
            rule_pack=state.rule_pack,
        )
        state.context_artifact = {
            **state.context_artifact,
            "articleDossier": artifact["articleDossier"],
            "contextPacks": artifact["contextPacks"],
        }
        state.progress.succeed(
            DraftRunStepKey.RULE_PACK,
            with_progress_payload(artifact, rule_progress),
        )

    def material_plan(self, state: DraftWorkflowState) -> None:
        state.progress.start(DraftRunStepKey.MATERIAL_PLAN)
        material_progress = state.progress.operation_sink(DraftRunStepKey.MATERIAL_PLAN, total_operations=1)
        settings = get_settings()
        provider_dossier = self._planning_dossier(state, "materialPlan")
        material_budget = _budget_estimate(
            operation_id="materialPlan",
            draft_run_step="materialPlan",
            provider_input=provider_dossier.provider_input(),
            execution_mode=settings.draft_run_execution_mode,
            model=_selected_model(settings.draft_strategy_model, settings.openrouter_default_model),
        )
        material_progress.start_operation(
            "materialPlan",
            kind="materialPlan",
            label="Material plan",
            model_role=DraftModelRole.STRATEGY.value,
            selected_model=_selected_model(settings.draft_strategy_model, settings.openrouter_default_model),
            prompt_char_estimate=material_budget["promptCharEstimate"],
            approx_token_estimate=material_budget["approxTokenEstimate"],
            stale_after_seconds=_provider_stale_after_seconds(settings.draft_run_execution_mode),
        )
        try:
            result = self._services.material_plan_service.create(
                context_summary=state.context_summary,
                rule_pack=state.rule_pack,
                provider_dossier=provider_dossier,
                context_artifact=state.context_artifact,
            )
        except Exception as exc:
            material_progress.fail_operation("materialPlan", str(exc))
            raise
        state.progress.add_ai_run_ids(
            result.ai_run_ids or ([result.ai_run_id] if result.ai_run_id else [])
        )
        material_progress.complete_operation(
            "materialPlan",
            ai_run_id=result.ai_run_id,
            notes=["provider-runtime-recorded"],
        )
        state.material_plan = payload_section(result.artifact_payload, "materialPlan")
        state.progress.succeed(
            DraftRunStepKey.MATERIAL_PLAN,
            with_progress_payload(
                self._services.article_memory.attach(
                    result.artifact_payload,
                    context_artifact=state.context_artifact,
                    rule_pack=state.rule_pack,
                    material_plan=state.material_plan,
                ),
                material_progress,
            ),
        )

    def strategy(self, state: DraftWorkflowState) -> None:
        state.progress.start(DraftRunStepKey.STRATEGY)
        strategy_progress = state.progress.operation_sink(DraftRunStepKey.STRATEGY, total_operations=1)
        settings = get_settings()
        provider_dossier = self._planning_dossier(state, "strategy")
        strategy_budget = _budget_estimate(
            operation_id="strategy",
            profile_operation_id="draftStrategy",
            draft_run_step="strategy",
            provider_input=provider_dossier.provider_input(),
            execution_mode=settings.draft_run_execution_mode,
            model=_selected_model(settings.draft_strategy_model, settings.openrouter_default_model),
        )
        strategy_progress.start_operation(
            "draftStrategy",
            kind="draftStrategy",
            label="Draft strategy",
            model_role=DraftModelRole.STRATEGY.value,
            selected_model=_selected_model(settings.draft_strategy_model, settings.openrouter_default_model),
            prompt_char_estimate=strategy_budget["promptCharEstimate"],
            approx_token_estimate=strategy_budget["approxTokenEstimate"],
            stale_after_seconds=_provider_stale_after_seconds(settings.draft_run_execution_mode),
        )
        try:
            result = self._services.strategy_service.create(
                context_summary=state.context_summary,
                rule_pack=state.rule_pack,
                material_plan=state.material_plan,
                provider_dossier=provider_dossier,
                context_pack=context_pack_for_role(state.context_artifact, DraftModelRole.STRATEGY),
            )
        except Exception as exc:
            strategy_progress.fail_operation("draftStrategy", str(exc))
            raise
        state.progress.add_ai_run_id(result.ai_run_id)
        strategy_progress.complete_operation(
            "draftStrategy",
            ai_run_id=result.ai_run_id,
            notes=["provider-runtime-recorded"],
        )
        state.draft_strategy = payload_section(result.artifact_payload, "draftStrategy")
        state.progress.succeed(
            DraftRunStepKey.STRATEGY,
            with_progress_payload(
                self._services.article_memory.attach(
                    result.artifact_payload,
                    context_artifact=state.context_artifact,
                    rule_pack=state.rule_pack,
                    material_plan=state.material_plan,
                    draft_strategy=state.draft_strategy,
                ),
                strategy_progress,
            ),
        )

    def rhetorical_plans_phase(self, state: DraftWorkflowState) -> None:
        state.progress.start(DraftRunStepKey.RHETORICAL_PLANS)
        rhetorical_progress = state.progress.operation_sink(DraftRunStepKey.RHETORICAL_PLANS, total_operations=1)
        settings = get_settings()
        provider_dossier = self._planning_dossier(state, "rhetoricalPlans")
        rhetorical_budget = _budget_estimate(
            operation_id="rhetoricalPlans",
            draft_run_step="rhetoricalPlans",
            provider_input=provider_dossier.provider_input(),
            execution_mode=settings.draft_run_execution_mode,
            model=_selected_model(settings.draft_strategy_model, settings.openrouter_default_model),
        )
        rhetorical_progress.start_operation(
            "rhetoricalPlans",
            kind="rhetoricalPlans",
            label="Rhetorical plans",
            model_role=DraftModelRole.STRATEGY.value,
            selected_model=_selected_model(settings.draft_strategy_model, settings.openrouter_default_model),
            prompt_char_estimate=rhetorical_budget["promptCharEstimate"],
            approx_token_estimate=rhetorical_budget["approxTokenEstimate"],
            stale_after_seconds=_provider_stale_after_seconds(settings.draft_run_execution_mode),
        )
        try:
            result = self._services.rhetorical_plan_service.create(
                context_summary=state.context_summary,
                context_artifact=state.context_artifact,
                rule_pack=state.rule_pack,
                material_plan=state.material_plan,
                draft_strategy=state.draft_strategy,
                provider_dossier=provider_dossier,
            )
        except Exception as exc:
            rhetorical_progress.fail_operation("rhetoricalPlans", str(exc))
            raise
        state.progress.add_ai_run_ids(
            result.ai_run_ids or ([result.ai_run_id] if result.ai_run_id else [])
        )
        rhetorical_progress.complete_operation(
            "rhetoricalPlans",
            ai_run_id=result.ai_run_id,
            notes=["provider-runtime-recorded"],
        )
        state.rhetorical_plans = payload_section(result.artifact_payload, "rhetoricalPlanSet")
        state.progress.succeed(
            DraftRunStepKey.RHETORICAL_PLANS,
            with_progress_payload(
                self._services.article_memory.attach(
                    result.artifact_payload,
                    context_artifact=state.context_artifact,
                    rule_pack=state.rule_pack,
                    material_plan=state.material_plan,
                    draft_strategy=state.draft_strategy,
                    rhetorical_plans=state.rhetorical_plans,
                ),
                rhetorical_progress,
            ),
        )

    def draft(self, state: DraftWorkflowState) -> None:
        state.progress.start(DraftRunStepKey.DRAFT)
        draft_progress = state.progress.operation_sink(DraftRunStepKey.DRAFT)
        state.draft_result = self._services.draft_step_service.create(
            request=state.request,
            context_summary=state.context_summary,
            rule_pack=state.rule_pack,
            material_plan=state.material_plan,
            draft_strategy=state.draft_strategy,
            rhetorical_plans=state.rhetorical_plans,
            context_pack=context_pack_for_role(state.context_artifact, DraftModelRole.WRITER),
            provider_dossier_factory=WriterDossierFactory(self._context_access(state)),
            progress=draft_progress,
        )
        state.progress.add_ai_run_ids(state.draft_result.ai_run_ids)
        state.draft_artifact = state.draft_result.artifact_payload
        state.progress.succeed(
            DraftRunStepKey.DRAFT,
            with_progress_payload(
                self._services.article_memory.attach(
                    state.draft_artifact,
                    context_artifact=state.context_artifact,
                    rule_pack=state.rule_pack,
                    material_plan=state.material_plan,
                    draft_strategy=state.draft_strategy,
                    rhetorical_plans=state.rhetorical_plans,
                    draft_artifact=state.draft_artifact,
                ),
                draft_progress,
            ),
        )

    def validation(self, state: DraftWorkflowState) -> None:
        state.progress.start(DraftRunStepKey.VALIDATION)
        settings = get_settings()
        validation_runtime_guard = ValidationRuntimeGuard(
            ValidationRuntimeBudgetPolicy().profile_for(
                state.context_artifact,
                max_revision_iterations=settings.draft_revision_max_iterations,
                max_final_repair_iterations=settings.draft_final_repair_max_iterations,
            )
        )
        validation_progress = state.progress.operation_sink(
            DraftRunStepKey.VALIDATION,
            runtime_guard=validation_runtime_guard,
        )
        state.validation_result = self._services.validation_step_service.validate(
            request=state.request,
            context_summary=state.context_summary,
            draft_artifact=state.draft_artifact,
            context_artifact=state.context_artifact,
            rule_pack=state.rule_pack,
            material_plan=state.material_plan,
            draft_strategy=state.draft_strategy,
            progress=validation_progress,
        )
        state.progress.add_ai_run_ids(state.validation_result.ai_run_ids)
        state.validation_artifact = state.validation_result.artifact_payload
        state.final_draft = state.validation_result.final_draft or state.draft_result.final_draft
        state.progress.succeed(
            DraftRunStepKey.VALIDATION,
            with_progress_payload(
                self._services.article_memory.attach(
                    state.validation_artifact,
                    context_artifact=state.context_artifact,
                    rule_pack=state.rule_pack,
                    material_plan=state.material_plan,
                    draft_strategy=state.draft_strategy,
                    rhetorical_plans=state.rhetorical_plans,
                    draft_artifact=state.draft_artifact,
                    validation_artifact=state.validation_artifact,
                ),
                validation_progress,
            ),
        )

    def complete(self, state: DraftWorkflowState) -> None:
        if state.final_draft is None:
            quality_fidelity = self._quality_fidelity.build_from_run(
                self._services.repository.get(state.run_id),
                final_draft=None,
            )
            state.progress.complete(
                DraftRunStepKey.COMPLETE,
                {**candidate_selection_blocked_payload(state.draft_artifact), "qualityFidelity": quality_fidelity},
            )
            self._services.repository.set_run_status(
                state.run_id,
                DraftRunStatus.SUCCEEDED,
                ai_run_ids=state.progress.ai_run_ids,
            )
            return
        final_payload = draft_to_payload(state.final_draft)
        quality_fidelity = self._quality_fidelity.build_from_run(
            self._services.repository.get(state.run_id),
            final_draft=final_payload,
        )
        self._attach_validation_quality_fidelity(state, quality_fidelity)
        state.progress.complete(DraftRunStepKey.COMPLETE, {"status": "succeeded", "qualityFidelity": quality_fidelity})
        self._services.repository.set_run_status(
            state.run_id,
            DraftRunStatus.SUCCEEDED,
            final_draft=final_payload,
            ai_run_ids=state.progress.ai_run_ids,
        )

    def _attach_validation_quality_fidelity(self, state: DraftWorkflowState, quality_fidelity: dict[str, object]) -> None:
        loaded = self._services.repository.get(state.run_id)
        validation_payload = next(
            (
                dict(step.artifact_payload or {})
                for step in (loaded.steps if loaded else [])
                if step.key == DraftRunStepKey.VALIDATION
            ),
            {},
        )
        ranking_revision = dict(validation_payload.get("rankingRevision") or {})
        ranking_revision["qualityFidelity"] = quality_fidelity
        validation_payload["rankingRevision"] = ranking_revision
        state.progress.succeed(DraftRunStepKey.VALIDATION, validation_payload)

    def _planning_dossier(self, state: DraftWorkflowState, operation_id: str) -> ProviderDossier:
        return PlanningDossierFactory(self._context_access(state)).build(operation_id)

    def _context_access(self, state: DraftWorkflowState) -> DraftRunContextAccessService:
        run = self._services.repository.get(state.run_id)
        if run is None:
            raise RuntimeError(f"DraftRun not found while building provider dossier: {state.run_id}")
        return DraftRunContextAccessService.from_run(run)


def _payload_char_estimate(payload: dict[str, Any]) -> int:
    return len(json.dumps(payload, ensure_ascii=False, default=str))


def _selected_model(*models: str | None) -> str | None:
    for model in models:
        if model and model.strip():
            return model.strip()
    return None


def _provider_stale_after_seconds(execution_mode: str | None) -> int:
    mode = (execution_mode or "standard").strip().lower()
    if mode == "smoke":
        return 180
    if mode == "full":
        return 1200
    return 900


def _budget_estimate(
    *,
    operation_id: str,
    draft_run_step: str,
    provider_input: dict[str, Any],
    execution_mode: str | None,
    model: str | None,
    profile_operation_id: str | None = None,
) -> dict[str, int]:
    proof = ProviderInputBudgetGate().evaluate(
        operation_id=operation_id,
        profile_operation_id=profile_operation_id,
        draft_run_step=draft_run_step,
        provider_input=provider_input,
        execution_mode=execution_mode,
        model=model,
        model_role=DraftModelRole.STRATEGY.value,
    )
    return {
        "promptCharEstimate": proof.prompt_char_estimate,
        "approxTokenEstimate": proof.approx_token_estimate,
    }
