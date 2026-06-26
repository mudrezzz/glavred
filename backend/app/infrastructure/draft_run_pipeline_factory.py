from backend.app.application.ai_run_service import AiRunService
from backend.app.application.deterministic_draft_candidate_service import DeterministicDraftCandidateService
from backend.app.application.deterministic_draft_planning_service import DeterministicDraftPlanningService
from backend.app.application.deterministic_draft_service import DeterministicDraftService
from backend.app.application.deterministic_rhetorical_plan_service import DeterministicRhetoricalPlanService
from backend.app.application.draft_candidate_direction_service import DraftCandidateDirectionService
from backend.app.application.draft_candidate_generation_service import DraftCandidateGenerationService
from backend.app.application.draft_candidate_selection_service import DraftCandidateSelectionService
from backend.app.application.draft_material_plan_service import DraftMaterialPlanService
from backend.app.application.draft_rhetorical_plan_service import DraftRhetoricalPlanService
from backend.app.application.draft_run_pipeline import DraftRunPipeline
from backend.app.application.draft_strategy_service import DraftStrategyService
from backend.app.application.evidence_interpretation_service import EvidenceInterpretationService
from backend.app.application.source_research_plan_service import SourceResearchPlanService
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.openrouter_json_adapter import OpenRouterJsonAdapter
from backend.app.infrastructure.draft_run_pipeline_provider_services import build_public_evidence_step_service
from backend.app.infrastructure.draft_run_pipeline_validation_services import build_validation_step_service
from backend.app.infrastructure.sqlite_ai_run_repository import SqliteAiRunRepository
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.app.settings import BackendSettings


def build_draft_run_pipeline(settings: BackendSettings) -> DraftRunPipeline:
    ai_run_service = AiRunService(repository=SqliteAiRunRepository(settings.ai_run_audit_db_path))
    openrouter_validator = OpenRouterConfigValidator()
    openrouter_adapter = OpenRouterJsonAdapter()
    deterministic_planning_service = DeterministicDraftPlanningService()
    provider_kwargs = {"settings": settings, "ai_run_service": ai_run_service, "openrouter_validator": openrouter_validator, "openrouter_adapter": openrouter_adapter}
    return DraftRunPipeline(
        repository=SqliteDraftRunRepository(settings.draft_run_db_path),
        deterministic_draft_service=DeterministicDraftService(),
        material_plan_service=DraftMaterialPlanService(**provider_kwargs, deterministic_planning_service=deterministic_planning_service),
        strategy_service=DraftStrategyService(**provider_kwargs, deterministic_planning_service=deterministic_planning_service),
        source_research_plan_service=SourceResearchPlanService(**provider_kwargs),
        public_evidence_step_service=build_public_evidence_step_service(**provider_kwargs),
        rhetorical_plan_service=DraftRhetoricalPlanService(**provider_kwargs, deterministic_plan_service=DeterministicRhetoricalPlanService()),
        evidence_interpretation_service=EvidenceInterpretationService(**provider_kwargs),
        candidate_generation_service=DraftCandidateGenerationService(
            **provider_kwargs,
            direction_service=DraftCandidateDirectionService(),
            deterministic_candidate_service=DeterministicDraftCandidateService(),
            selection_service=DraftCandidateSelectionService(),
        ),
        validation_step_service=build_validation_step_service(**provider_kwargs),
    )
