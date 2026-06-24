from typing import Any

from backend.app.application.draft_quality_gate import DraftQualityGate
from backend.app.application.draft_rule_pack_compiler import DraftRulePackCompiler
from backend.app.application.draft_run_context_builder import build_draft_run_context_summary
from backend.app.application.draft_run_context_payloads import context_from_payload
from backend.app.application.draft_run_payloads import draft_to_payload, request_from_payload
from backend.app.application.deterministic_draft_service import DeterministicDraftService
from backend.app.application.deterministic_draft_planning_service import DeterministicDraftPlanningService
from backend.app.application.deterministic_draft_planning_step_services import DeterministicMaterialPlanStepService, DeterministicStrategyStepService
from backend.app.application.deterministic_rhetorical_plan_step_service import DeterministicRhetoricalPlanStepService
from backend.app.application.deterministic_source_research_step_service import DeterministicSourceResearchStepService
from backend.app.application.draft_candidate_generation_service import DraftCandidateGenerationService
from backend.app.application.draft_candidate_selection_block import candidate_selection_blocked_payload
from backend.app.application.draft_run_draft_step_service import LegacyDraftStepService
from backend.app.application.draft_public_evidence_step_service import PublicEvidenceStepService
from backend.app.application.draft_run_pipeline_ports import DraftRunPipelineRepository
from backend.app.application.draft_run_progress import DraftRunProgress
from backend.app.application.draft_source_ledger_builder import SourceLedgerBuilder
from backend.app.domain.draft_run import DraftRun, DraftRunStatus, DraftRunStepKey


class DraftRunPipeline:
    def __init__(
        self,
        repository: DraftRunPipelineRepository,
        deterministic_draft_service: DeterministicDraftService,
        rule_pack_compiler: DraftRulePackCompiler | None = None,
        material_plan_service: Any = None,
        strategy_service: Any = None,
        source_research_plan_service: Any = None,
        public_evidence_step_service: PublicEvidenceStepService | None = None,
        rhetorical_plan_service: Any = None,
        candidate_generation_service: DraftCandidateGenerationService | None = None,
        source_ledger_builder: SourceLedgerBuilder | None = None,
        quality_gate: DraftQualityGate | None = None,
    ) -> None:
        self._repository = repository
        self._rule_pack_compiler = rule_pack_compiler or DraftRulePackCompiler()
        self._source_ledger_builder = source_ledger_builder or SourceLedgerBuilder()
        self._quality_gate = quality_gate or DraftQualityGate()
        fallback = DeterministicDraftPlanningService()
        self._material_plan_service = material_plan_service or DeterministicMaterialPlanStepService(fallback)
        self._strategy_service = strategy_service or DeterministicStrategyStepService(fallback)
        self._source_research_plan_service = source_research_plan_service or DeterministicSourceResearchStepService()
        self._public_evidence_step_service = public_evidence_step_service or PublicEvidenceStepService()
        self._rhetorical_plan_service = rhetorical_plan_service or DeterministicRhetoricalPlanStepService()
        self._draft_step_service = candidate_generation_service or LegacyDraftStepService(deterministic_draft_service)

    def execute(self, run_id: str) -> DraftRun:
        run = self._repository.get(run_id)
        if run is None:
            raise ValueError(f"DraftRun {run_id} not found")
        self._repository.set_run_status(run_id, DraftRunStatus.RUNNING)
        progress = DraftRunProgress(self._repository, run_id)
        try:
            request = request_from_payload(run.request_payload)
            context_summary = build_draft_run_context_summary(request, context_from_payload(run.request_payload))
            source_ledger = self._source_ledger_builder.build(context_summary, request).to_payload()
            context_artifact = {**context_summary, "sourceLedger": source_ledger}
            progress.complete(DraftRunStepKey.CONTEXT, context_artifact)
            source_result = self._source_research_plan_service.create(request=request, context_artifact=context_artifact)
            progress.add_ai_run_id(source_result.ai_run_id)
            context_artifact = {**context_artifact, **source_result.artifact_payload}
            progress.complete(DraftRunStepKey.SOURCE_INTENT, source_result.artifact_payload)
            progress.start(DraftRunStepKey.PUBLIC_EVIDENCE)
            public_evidence_result = self._public_evidence_step_service.run(
                source_intent_artifact=source_result.artifact_payload,
                context_artifact=context_artifact,
            )
            progress.add_ai_run_ids(public_evidence_result.ai_run_ids)
            context_artifact = public_evidence_result.context_artifact
            progress.succeed(DraftRunStepKey.PUBLIC_EVIDENCE, public_evidence_result.artifact_payload)
            quality_gate_result = self._quality_gate.evaluate(context_artifact)
            progress.complete(DraftRunStepKey.FEASIBILITY, quality_gate_result.feasibility_report)
            progress.complete(DraftRunStepKey.POST_CONTRACT, quality_gate_result.post_contract)
            if quality_gate_result.blocked:
                progress.complete(DraftRunStepKey.COMPLETE, quality_gate_result.complete_payload or {"status": "blocked"})
                self._repository.set_run_status(run_id, DraftRunStatus.SUCCEEDED, ai_run_ids=[])
                return self._loaded(run_id)
            context_artifact = quality_gate_result.context_artifact
            rule_pack = self._rule_pack_compiler.compile(context_artifact).to_payload()
            progress.complete(DraftRunStepKey.RULE_PACK, rule_pack)
            progress.start(DraftRunStepKey.MATERIAL_PLAN)
            material_plan_result = self._material_plan_service.create(context_summary=context_summary, rule_pack=rule_pack)
            progress.add_ai_run_id(material_plan_result.ai_run_id)
            material_plan = _payload(material_plan_result.artifact_payload, "materialPlan")
            progress.succeed(DraftRunStepKey.MATERIAL_PLAN, material_plan_result.artifact_payload)
            progress.start(DraftRunStepKey.STRATEGY)
            strategy_result = self._strategy_service.create(context_summary=context_summary, rule_pack=rule_pack, material_plan=material_plan)
            progress.add_ai_run_id(strategy_result.ai_run_id)
            progress.succeed(DraftRunStepKey.STRATEGY, strategy_result.artifact_payload)
            draft_strategy = _payload(strategy_result.artifact_payload, "draftStrategy")
            progress.start(DraftRunStepKey.RHETORICAL_PLANS)
            plan_result = self._rhetorical_plan_service.create(
                context_summary=context_summary,
                context_artifact=context_artifact,
                rule_pack=rule_pack,
                material_plan=material_plan,
                draft_strategy=draft_strategy,
            )
            progress.add_ai_run_id(plan_result.ai_run_id)
            rhetorical_plans = _payload(plan_result.artifact_payload, "rhetoricalPlanSet")
            progress.succeed(DraftRunStepKey.RHETORICAL_PLANS, plan_result.artifact_payload)
            progress.start(DraftRunStepKey.DRAFT)
            draft_result = self._draft_step_service.create(
                request=request,
                context_summary=context_summary,
                rule_pack=rule_pack,
                material_plan=material_plan,
                draft_strategy=draft_strategy,
                rhetorical_plans=rhetorical_plans,
            )
            progress.add_ai_run_ids(draft_result.ai_run_ids)
            progress.succeed(DraftRunStepKey.DRAFT, draft_result.artifact_payload)
            if draft_result.final_draft is None:
                progress.complete(DraftRunStepKey.VALIDATION, {"status": "not-run", "reason": "draft candidate selection blocked"})
                progress.complete(DraftRunStepKey.COMPLETE, candidate_selection_blocked_payload(draft_result.artifact_payload))
                self._repository.set_run_status(run_id, DraftRunStatus.SUCCEEDED, ai_run_ids=progress.ai_run_ids)
                return self._loaded(run_id)
            draft_payload = draft_to_payload(draft_result.final_draft)
            progress.complete(DraftRunStepKey.VALIDATION, {"status": "placeholder-passed", "checks": ["structure", "audience", "rules"]})
            progress.complete(DraftRunStepKey.COMPLETE, {"status": "succeeded"})
            self._repository.set_run_status(run_id, DraftRunStatus.SUCCEEDED, final_draft=draft_payload, ai_run_ids=progress.ai_run_ids)
        except Exception as exc:
            safe_error = str(exc)[:500] or "Draft run failed"
            progress.fail_current(safe_error)
            self._repository.set_run_status(run_id, DraftRunStatus.FAILED, error=safe_error)
        return self._loaded(run_id)

    def _loaded(self, run_id: str) -> DraftRun:
        loaded = self._repository.get(run_id)
        if loaded is None:
            raise ValueError(f"DraftRun {run_id} disappeared")
        return loaded
def _payload(artifact: dict[str, Any], key: str) -> dict[str, Any]:
    value = artifact.get(key)
    return value if isinstance(value, dict) else {}
