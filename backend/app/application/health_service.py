from backend.app.domain.health import BackendHealth, OpenRouterConfigurationStatus
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings


class BackendHealthService:
    def __init__(
        self,
        settings: BackendSettings,
        openrouter_validator: OpenRouterConfigValidator,
    ) -> None:
        self._settings = settings
        self._openrouter_validator = openrouter_validator

    def liveness(self) -> dict[str, str]:
        health = BackendHealth(environment=self._settings.environment)
        return {
            "status": health.status,
            "service": health.service,
            "environment": health.environment,
        }

    def readiness(self) -> dict[str, object]:
        openrouter_status = self._openrouter_validator.evaluate(self._settings)
        return {
            "status": "ok",
            "service": "glavred-backend",
            "environment": self._settings.environment,
            "openRouter": self._serialize_openrouter_status(openrouter_status),
            "aiRunAudit": {
                "configured": True,
                "storage": "sqlite",
            },
        }

    def _serialize_openrouter_status(
        self,
        status: OpenRouterConfigurationStatus,
    ) -> dict[str, object]:
        return {
            "configured": status.configured,
            "baseUrl": status.base_url,
            "defaultModelConfigured": status.default_model_configured,
            "appNameConfigured": status.app_name_configured,
            "httpRefererConfigured": status.http_referer_configured,
        }
