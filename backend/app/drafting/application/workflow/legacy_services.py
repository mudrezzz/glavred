"""Owner: drafting.application.workflow

Used by: legacy DraftRun workflow factory while step services are migrated.
Does not own: provider adapters, prompt text, API request parsing, SQLite persistence.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.app.drafting.application.planning.deterministic_draft_planning_service import (
    DeterministicDraftPlanningService,
)
from backend.app.drafting.application.planning.deterministic_draft_planning_step_services import (
    DeterministicMaterialPlanStepService,
    DeterministicStrategyStepService,
)
from backend.app.drafting.application.evidence.deterministic_evidence_interpretation_step_service import (
    DeterministicEvidenceInterpretationStepService,
)
from backend.app.drafting.application.planning.deterministic_rhetorical_plan_step_service import (
    DeterministicRhetoricalPlanStepService,
)
from backend.app.drafting.application.evidence.deterministic_source_research_step_service import (
    DeterministicSourceResearchStepService,
)
from backend.app.drafting.application.generation.deterministic_draft_service import DeterministicDraftService
from backend.app.drafting.application.artifacts.draft_article_memory_service import DraftArticleMemoryService
from backend.app.drafting.application.generation.draft_candidate_generation_service import DraftCandidateGenerationService
from backend.app.drafting.application.evidence.draft_public_evidence_step_service import PublicEvidenceStepService
from backend.app.drafting.application.evidence.draft_quality_gate import DraftQualityGate
from backend.app.drafting.application.evidence.draft_rule_pack_compiler import DraftRulePackCompiler
from backend.app.application.draft_run_draft_step_service import LegacyDraftStepService
from backend.app.application.draft_run_pipeline_ports import DraftRunPipelineRepository
from backend.app.drafting.application.artifacts.draft_source_ledger_builder import SourceLedgerBuilder
from backend.app.drafting.application.validation.draft_validation_step_service import DraftValidationStepService


@dataclass
class LegacyDraftWorkflowServices:
    repository: DraftRunPipelineRepository
    rule_pack_compiler: DraftRulePackCompiler
    source_ledger_builder: SourceLedgerBuilder
    quality_gate: DraftQualityGate
    material_plan_service: Any
    strategy_service: Any
    source_research_plan_service: Any
    public_evidence_step_service: PublicEvidenceStepService
    rhetorical_plan_service: Any
    draft_step_service: Any
    validation_step_service: DraftValidationStepService
    article_memory: DraftArticleMemoryService
    evidence_interpretation_service: Any

    @classmethod
    def create(
        cls,
        *,
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
    ) -> LegacyDraftWorkflowServices:
        fallback = DeterministicDraftPlanningService()
        return cls(
            repository=repository,
            rule_pack_compiler=rule_pack_compiler or DraftRulePackCompiler(),
            source_ledger_builder=source_ledger_builder or SourceLedgerBuilder(),
            quality_gate=quality_gate or DraftQualityGate(),
            material_plan_service=material_plan_service
            or DeterministicMaterialPlanStepService(fallback),
            strategy_service=strategy_service or DeterministicStrategyStepService(fallback),
            source_research_plan_service=source_research_plan_service
            or DeterministicSourceResearchStepService(),
            public_evidence_step_service=public_evidence_step_service or PublicEvidenceStepService(),
            rhetorical_plan_service=rhetorical_plan_service or DeterministicRhetoricalPlanStepService(),
            draft_step_service=candidate_generation_service
            or LegacyDraftStepService(deterministic_draft_service),
            validation_step_service=validation_step_service or DraftValidationStepService(),
            article_memory=article_memory_service or DraftArticleMemoryService(),
            evidence_interpretation_service=evidence_interpretation_service
            or DeterministicEvidenceInterpretationStepService(),
        )
