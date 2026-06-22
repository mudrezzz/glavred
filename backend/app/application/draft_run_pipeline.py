from typing import Any

from backend.app.application.draft_quality_gate import DraftQualityGate
from backend.app.application.draft_rule_pack_compiler import DraftRulePackCompiler
from backend.app.application.draft_run_context_builder import build_draft_run_context_summary
from backend.app.application.draft_run_context_payloads import context_from_payload
from backend.app.application.draft_run_payloads import draft_to_payload, request_from_payload
from backend.app.application.deterministic_draft_service import DeterministicDraftService
from backend.app.application.deterministic_draft_planning_service import DeterministicDraftPlanningService
from backend.app.application.deterministic_draft_planning_step_services import (
    DeterministicMaterialPlanStepService,
    DeterministicStrategyStepService,
)
from backend.app.application.draft_candidate_generation_service import DraftCandidateGenerationService
from backend.app.application.draft_run_draft_step_service import LegacyDraftStepService
from backend.app.application.draft_run_pipeline_ports import DraftRunPipelineRepository
from backend.app.application.draft_source_ledger_builder import SourceLedgerBuilder
from backend.app.domain.draft_run import (
    DraftRun,
    DraftRunStatus,
    DraftRunStepKey,
    DraftRunStepStatus,
)


class DraftRunPipeline:
    def __init__(
        self,
        repository: DraftRunPipelineRepository,
        deterministic_draft_service: DeterministicDraftService,
        rule_pack_compiler: DraftRulePackCompiler | None = None,
        material_plan_service: Any = None,
        strategy_service: Any = None,
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
        self._draft_step_service = candidate_generation_service or LegacyDraftStepService(deterministic_draft_service)

    def execute(self, run_id: str) -> DraftRun:
        run = self._repository.get(run_id)
        if run is None:
            raise ValueError(f"DraftRun {run_id} not found")
        self._repository.set_run_status(run_id, DraftRunStatus.RUNNING)
        try:
            request = request_from_payload(run.request_payload)
            context_summary = build_draft_run_context_summary(request, context_from_payload(run.request_payload))
            source_ledger = self._source_ledger_builder.build(context_summary, request).to_payload()
            context_artifact = {**context_summary, "sourceLedger": source_ledger}
            self._complete_step(run_id, DraftRunStepKey.CONTEXT, context_artifact)
            quality_gate_result = self._quality_gate.evaluate(context_artifact)
            self._complete_step(run_id, DraftRunStepKey.FEASIBILITY, quality_gate_result.feasibility_report)
            self._complete_step(run_id, DraftRunStepKey.POST_CONTRACT, quality_gate_result.post_contract)
            if quality_gate_result.blocked:
                self._complete_step(run_id, DraftRunStepKey.COMPLETE, quality_gate_result.complete_payload or {"status": "blocked"})
                self._repository.set_run_status(run_id, DraftRunStatus.SUCCEEDED, ai_run_ids=[])
                return self._loaded(run_id)
            context_artifact = quality_gate_result.context_artifact
            rule_pack = self._rule_pack_compiler.compile(context_artifact).to_payload()
            self._complete_step(run_id, DraftRunStepKey.RULE_PACK, rule_pack)
            ai_run_ids: list[str] = []
            material_plan_result = self._material_plan_service.create(
                context_summary=context_summary,
                rule_pack=rule_pack,
            )
            ai_run_ids.extend(_ai_ids(material_plan_result.ai_run_id))
            material_plan = _payload(material_plan_result.artifact_payload, "materialPlan")
            self._complete_step(run_id, DraftRunStepKey.MATERIAL_PLAN, material_plan_result.artifact_payload)
            strategy_result = self._strategy_service.create(
                context_summary=context_summary,
                rule_pack=rule_pack,
                material_plan=material_plan,
            )
            ai_run_ids.extend(_ai_ids(strategy_result.ai_run_id))
            self._complete_step(run_id, DraftRunStepKey.STRATEGY, strategy_result.artifact_payload)
            draft_result = self._draft_step_service.create(
                request=request,
                context_summary=context_summary,
                rule_pack=rule_pack,
                material_plan=material_plan,
                draft_strategy=_payload(strategy_result.artifact_payload, "draftStrategy"),
            )
            ai_run_ids.extend(draft_result.ai_run_ids)
            draft_payload = draft_to_payload(draft_result.final_draft)
            self._complete_step(run_id, DraftRunStepKey.DRAFT, draft_result.artifact_payload)
            self._complete_step(
                run_id,
                DraftRunStepKey.VALIDATION,
                {
                    "status": "placeholder-passed",
                    "checks": ["structure", "audience", "rules"],
                },
            )
            self._complete_step(run_id, DraftRunStepKey.COMPLETE, {"status": "succeeded"})
            self._repository.set_run_status(run_id, DraftRunStatus.SUCCEEDED, final_draft=draft_payload, ai_run_ids=ai_run_ids)
        except Exception as exc:
            self._repository.set_run_status(
                run_id,
                DraftRunStatus.FAILED,
                error=(str(exc)[:500] or "Draft run failed"),
            )
        return self._loaded(run_id)

    def _complete_step(
        self,
        run_id: str,
        key: DraftRunStepKey,
        artifact_payload: dict[str, Any],
    ) -> None:
        self._repository.set_step_status(run_id, key, DraftRunStepStatus.RUNNING)
        self._repository.set_step_status(run_id, key, DraftRunStepStatus.SUCCEEDED, artifact_payload=artifact_payload)

    def _loaded(self, run_id: str) -> DraftRun:
        loaded = self._repository.get(run_id)
        if loaded is None:
            raise ValueError(f"DraftRun {run_id} disappeared")
        return loaded

def _payload(artifact: dict[str, Any], key: str) -> dict[str, Any]:
    value = artifact.get(key)
    return value if isinstance(value, dict) else {}

def _ai_ids(ai_run_id: str | None) -> list[str]:
    return [ai_run_id] if ai_run_id else []
