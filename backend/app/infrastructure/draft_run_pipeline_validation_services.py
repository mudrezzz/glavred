from backend.app.application.ai_run_service import AiRunService
from backend.app.application.draft_directed_revision_service import DraftDirectedRevisionService
from backend.app.application.draft_editorial_critique_service import DraftEditorialCritiqueService
from backend.app.application.draft_final_quality_gate import DraftFinalQualityGateService
from backend.app.application.draft_final_quality_review_service import DraftFinalQualityReviewService
from backend.app.application.draft_llm_validation_service import DraftLlmValidationService
from backend.app.application.draft_pairwise_ranking_service import DraftPairwiseRankingService
from backend.app.application.draft_ranking_revision_service import DraftRankingRevisionService
from backend.app.application.draft_revision_loop_config import revision_iteration_limit
from backend.app.application.draft_validation_step_service import DraftValidationStepService
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
            max_iterations=revision_iteration_limit(settings),
        ),
    )
