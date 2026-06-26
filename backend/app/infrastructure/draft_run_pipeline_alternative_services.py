from backend.app.application.ai_run_service import AiRunService
from backend.app.application.draft_alternative_angle_candidate_service import DraftAlternativeAngleCandidateService
from backend.app.application.draft_alternative_angle_route_service import DraftAlternativeAngleRouteService
from backend.app.application.draft_alternative_angle_tournament_service import DraftAlternativeAngleTournamentService
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.openrouter_json_adapter import OpenRouterJsonAdapter
from backend.app.settings import BackendSettings


def build_alternative_angle_tournament_service(
    *,
    settings: BackendSettings,
    ai_run_service: AiRunService,
    openrouter_validator: OpenRouterConfigValidator,
    openrouter_adapter: OpenRouterJsonAdapter,
) -> DraftAlternativeAngleTournamentService:
    provider_kwargs = {
        "settings": settings,
        "ai_run_service": ai_run_service,
        "openrouter_validator": openrouter_validator,
        "openrouter_adapter": openrouter_adapter,
    }
    return DraftAlternativeAngleTournamentService(
        route_service=DraftAlternativeAngleRouteService(**provider_kwargs),
        candidate_service=DraftAlternativeAngleCandidateService(**provider_kwargs),
    )
