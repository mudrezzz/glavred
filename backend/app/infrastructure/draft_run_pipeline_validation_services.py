from backend.app.application.ai_run_service import AiRunService
from backend.app.application.draft_directed_revision_service import DraftDirectedRevisionService
from backend.app.application.draft_llm_validation_service import DraftLlmValidationService
from backend.app.application.draft_pairwise_ranking_service import DraftPairwiseRankingService
from backend.app.application.draft_ranking_revision_service import DraftRankingRevisionService
from backend.app.application.draft_validation_step_service import DraftValidationStepService
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
    return DraftValidationStepService(
        llm_validator=DraftLlmValidationService(
            settings=settings,
            ai_run_service=ai_run_service,
            openrouter_validator=openrouter_validator,
            openrouter_adapter=openrouter_adapter,
        ),
        ranking_revision_service=DraftRankingRevisionService(
            ranking_service=DraftPairwiseRankingService(
                settings=settings,
                ai_run_service=ai_run_service,
                openrouter_validator=openrouter_validator,
                openrouter_adapter=openrouter_adapter,
            ),
            revision_service=DraftDirectedRevisionService(
                settings=settings,
                ai_run_service=ai_run_service,
                openrouter_validator=openrouter_validator,
                openrouter_adapter=openrouter_adapter,
            ),
        ),
    )
