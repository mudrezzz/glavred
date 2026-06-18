from backend.app.domain.health import OpenRouterConfigurationStatus
from backend.app.settings import BackendSettings


class OpenRouterConfigValidator:
    def evaluate(self, settings: BackendSettings) -> OpenRouterConfigurationStatus:
        default_model_configured = settings.has_openrouter_default_model
        app_name_configured = bool(settings.openrouter_app_name.strip())
        http_referer_configured = bool(settings.openrouter_http_referer.strip())
        configured = settings.has_openrouter_api_key and default_model_configured

        return OpenRouterConfigurationStatus(
            configured=configured,
            base_url=settings.openrouter_base_url,
            default_model_configured=default_model_configured,
            app_name_configured=app_name_configured,
            http_referer_configured=http_referer_configured,
        )
