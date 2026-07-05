from typing import Any

from backend.app.application.deterministic_draft_service import DeterministicDraftService
from backend.app.drafting.application.artifacts.draft_article_memory_service import DraftArticleMemoryService
from backend.app.application.draft_candidate_generation_service import DraftCandidateGenerationService
from backend.app.drafting.application.evidence.draft_public_evidence_step_service import PublicEvidenceStepService
from backend.app.drafting.application.evidence.draft_quality_gate import DraftQualityGate
from backend.app.drafting.application.evidence.draft_rule_pack_compiler import DraftRulePackCompiler
from backend.app.application.draft_run_pipeline_ports import DraftRunPipelineRepository
from backend.app.drafting.application.artifacts.draft_source_ledger_builder import SourceLedgerBuilder
from backend.app.application.draft_validation_step_service import DraftValidationStepService
from backend.app.domain.draft_run import DraftRun
from backend.app.drafting.application.workflow.legacy_workflow import build_legacy_draft_workflow
from backend.app.drafting.application.workflow.workflow import DraftWorkflow


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
        validation_step_service: DraftValidationStepService | None = None,
        article_memory_service: DraftArticleMemoryService | None = None,
        evidence_interpretation_service: Any = None,
    ) -> None:
        self._workflow: DraftWorkflow = build_legacy_draft_workflow(
            repository=repository,
            deterministic_draft_service=deterministic_draft_service,
            rule_pack_compiler=rule_pack_compiler,
            material_plan_service=material_plan_service,
            strategy_service=strategy_service,
            source_research_plan_service=source_research_plan_service,
            public_evidence_step_service=public_evidence_step_service,
            rhetorical_plan_service=rhetorical_plan_service,
            candidate_generation_service=candidate_generation_service,
            source_ledger_builder=source_ledger_builder,
            quality_gate=quality_gate,
            validation_step_service=validation_step_service,
            article_memory_service=article_memory_service,
            evidence_interpretation_service=evidence_interpretation_service,
        )

    def execute(self, run_id: str) -> DraftRun:
        return self._workflow.execute(run_id)
