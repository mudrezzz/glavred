from dataclasses import dataclass


@dataclass(frozen=True)
class BackendHealth:
    environment: str
    status: str = "ok"
    service: str = "glavred-backend"


@dataclass(frozen=True)
class OpenRouterConfigurationStatus:
    configured: bool
    base_url: str
    default_model_configured: bool
    app_name_configured: bool
    http_referer_configured: bool
