from typing import Any

from backend.app.settings import BackendSettings


def safe_provider_error(settings: BackendSettings, error: Exception, *, limit: int = 180) -> str:
    message = str(error)
    if settings.openrouter_api_key:
        token = settings.openrouter_api_key.get_secret_value()
        if token:
            message = message.replace(token, "[redacted]")
    return f"{error.__class__.__name__}: {message[:limit]}"


def raw_response_excerpt(error: Exception) -> str | None:
    value: Any = getattr(error, "raw_response_excerpt", None)
    return str(value) if value else None
