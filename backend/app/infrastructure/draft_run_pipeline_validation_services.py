from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.revision.draft_directed_revision_service import DraftDirectedRevisionService
from backend.app.drafting.application.validation.draft_editorial_critique_service import DraftEditorialCritiqueService
from backend.app.drafting.application.final_quality.draft_final_quality_gate import DraftFinalQualityGateService
from backend.app.drafting.application.final_quality.draft_final_quality_review_service import DraftFinalQualityReviewService
from backend.app.drafting.application.validation.draft_llm_validation_service import DraftLlmValidationService
from backend.app.drafting.application.revision.draft_pairwise_ranking_service import DraftPairwiseRankingService
from backend.app.drafting.application.revision.draft_ranking_revision_service import DraftRankingRevisionService
from backend.app.drafting.application.revision.draft_revision_loop_config import RevisionLoopConfigPolicy
from backend.app.drafting.application.validation.draft_validation_step_service import DraftValidationStepService
from backend.app.infrastructure.draft_run_pipeline_alternative_services import build_alternative_angle_tournament_service
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.openrouter_json_adapter import OpenRouterJsonAdapter
from backend.app.settings import BackendSettings


def build_validation_step_service(
    *,
    settings: BackendSettings,
    ai_run_service: AiRunService,
    openrouter_validator: OpenRouterConfigValidator,
    openrouter_adapter: OpenRouterJsonAdapter,
) -> DraftValidationStepService:
    provider_kwargs = {
        "settings": settings,
        "ai_run_service": ai_run_service,
        "openrouter_validator": openrouter_validator,
        "openrouter_adapter": openrouter_adapter,
    }
    return DraftValidationStepService(
        llm_validator=DraftLlmValidationService(**provider_kwargs),
        editorial_critic=DraftEditorialCritiqueService(**provider_kwargs),
        alternative_tournament=build_alternative_angle_tournament_service(**provider_kwargs),
        ranking_revision_service=DraftRankingRevisionService(
            ranking_service=DraftPairwiseRankingService(**provider_kwargs),
            revision_service=DraftDirectedRevisionService(**provider_kwargs),
            final_quality_gate=DraftFinalQualityGateService(
                revision_service=DraftDirectedRevisionService(**provider_kwargs),
                review_service=DraftFinalQualityReviewService(**provider_kwargs),
                max_repair_iterations=max(1, int(settings.draft_final_repair_max_iterations or 1)),
            ),
            max_iterations=RevisionLoopConfigPolicy().revision_iteration_limit(settings),
        ),
    )
