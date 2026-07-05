from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.evidence.draft_public_evidence_step_service import PublicEvidenceStepService
from backend.app.drafting.application.evidence.external_evidence_synthesis_service import ExternalEvidenceSynthesisService
from backend.app.drafting.application.evidence.openrouter_public_search_service import OpenRouterPublicSearchService
from backend.app.drafting.application.evidence.public_evidence_retrieval_service import PublicEvidenceRetrievalService
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.openrouter_json_adapter import OpenRouterJsonAdapter
from backend.app.infrastructure.openrouter_web_search_adapter import OpenRouterWebSearchAdapter
from backend.app.infrastructure.public_url_reader import HttpxPublicUrlReader
from backend.app.settings import BackendSettings


def build_public_evidence_step_service(
    *,
    settings: BackendSettings,
    ai_run_service: AiRunService,
    openrouter_validator: OpenRouterConfigValidator,
    openrouter_adapter: OpenRouterJsonAdapter,
) -> PublicEvidenceStepService:
    return PublicEvidenceStepService(
        public_evidence_service=PublicEvidenceRetrievalService(
            url_reader=HttpxPublicUrlReader(),
            search_adapter=OpenRouterPublicSearchService(
                settings=settings,
                ai_run_service=ai_run_service,
                openrouter_validator=openrouter_validator,
                web_search_adapter=OpenRouterWebSearchAdapter(),
            ),
        ),
        external_evidence_synthesis_service=ExternalEvidenceSynthesisService(
            settings=settings,
            ai_run_service=ai_run_service,
            openrouter_validator=openrouter_validator,
            openrouter_adapter=openrouter_adapter,
        ),
    )
