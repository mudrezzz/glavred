"""Owner: drafting.application.workflow

Used by: legacy DraftRun workflow factory during behavior-preserving migration.
Does not own: provider adapters, prompt text, API request parsing, SQLite persistence.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from backend.app.drafting.application.artifacts.draft_context_pack_builder import context_pack_for_role
from backend.app.drafting.application.generation.draft_candidate_selection_block import candidate_selection_blocked_payload
from backend.app.drafting.application.artifacts.draft_run_context_builder import build_draft_run_context_summary
from backend.app.drafting.application.artifacts.draft_run_context_payloads import context_from_payload
from backend.app.drafting.application.artifacts.draft_run_payloads import draft_to_payload, payload_section
from backend.app.drafting.application.artifacts.draft_run_budget_resolver import resolve_draft_run_budget
from backend.app.application.draft_run_step_progress_payload import with_progress_payload
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.domain.draft_run import DraftRunStatus
from backend.app.domain.draft_run_steps import DraftRunStepKey
from backend.app.drafting.application.operations.validation_runtime_budget import (
    ValidationRuntimeBudgetPolicy,
    ValidationRuntimeGuard,
)
from backend.app.drafting.application.workflow.legacy_services import LegacyDraftWorkflowServices
from backend.app.drafting.application.workflow.registry import DraftStepRegistry, DraftWorkflowPhase
from backend.app.drafting.application.workflow.state import DraftWorkflowState
from backend.app.settings import get_settings


class LegacyDraftWorkflowPhaseBuilder:
    def __init__(self, services: LegacyDraftWorkflowServices) -> None:
        self._services = services

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
            state.progress.complete(
                DraftRunStepKey.COMPLETE,
                result.complete_payload or {"status": "blocked"},
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
        result = self._services.material_plan_service.create(
            context_summary=state.context_summary,
            rule_pack=state.rule_pack,
            context_artifact=state.context_artifact,
        )
        state.progress.add_ai_run_ids(
            result.ai_run_ids or ([result.ai_run_id] if result.ai_run_id else [])
        )
        state.material_plan = payload_section(result.artifact_payload, "materialPlan")
        state.progress.succeed(
            DraftRunStepKey.MATERIAL_PLAN,
            self._services.article_memory.attach(
                result.artifact_payload,
                context_artifact=state.context_artifact,
                rule_pack=state.rule_pack,
                material_plan=state.material_plan,
            ),
        )

    def strategy(self, state: DraftWorkflowState) -> None:
        state.progress.start(DraftRunStepKey.STRATEGY)
        result = self._services.strategy_service.create(
            context_summary=state.context_summary,
            rule_pack=state.rule_pack,
            material_plan=state.material_plan,
            context_pack=context_pack_for_role(state.context_artifact, DraftModelRole.STRATEGY),
        )
        state.progress.add_ai_run_id(result.ai_run_id)
        state.draft_strategy = payload_section(result.artifact_payload, "draftStrategy")
        state.progress.succeed(
            DraftRunStepKey.STRATEGY,
            self._services.article_memory.attach(
                result.artifact_payload,
                context_artifact=state.context_artifact,
                rule_pack=state.rule_pack,
                material_plan=state.material_plan,
                draft_strategy=state.draft_strategy,
            ),
        )

    def rhetorical_plans_phase(self, state: DraftWorkflowState) -> None:
        state.progress.start(DraftRunStepKey.RHETORICAL_PLANS)
        result = self._services.rhetorical_plan_service.create(
            context_summary=state.context_summary,
            context_artifact=state.context_artifact,
            rule_pack=state.rule_pack,
            material_plan=state.material_plan,
            draft_strategy=state.draft_strategy,
        )
        state.progress.add_ai_run_ids(
            result.ai_run_ids or ([result.ai_run_id] if result.ai_run_id else [])
        )
        state.rhetorical_plans = payload_section(result.artifact_payload, "rhetoricalPlanSet")
        state.progress.succeed(
            DraftRunStepKey.RHETORICAL_PLANS,
            self._services.article_memory.attach(
                result.artifact_payload,
                context_artifact=state.context_artifact,
                rule_pack=state.rule_pack,
                material_plan=state.material_plan,
                draft_strategy=state.draft_strategy,
                rhetorical_plans=state.rhetorical_plans,
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
            state.progress.complete(
                DraftRunStepKey.COMPLETE,
                candidate_selection_blocked_payload(state.draft_artifact),
            )
            self._services.repository.set_run_status(
                state.run_id,
                DraftRunStatus.SUCCEEDED,
                ai_run_ids=state.progress.ai_run_ids,
            )
            return
        state.progress.complete(DraftRunStepKey.COMPLETE, {"status": "succeeded"})
        self._services.repository.set_run_status(
            state.run_id,
            DraftRunStatus.SUCCEEDED,
            final_draft=draft_to_payload(state.final_draft),
            ai_run_ids=state.progress.ai_run_ids,
        )
