"""Owner: drafting.application.operations

Used by: DraftRun operation migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.settings import BackendSettings


class DraftProviderErrorUtilsComponent:
    """Owns migrated helper behavior; module-level aliases remain compatibility-only."""

    @staticmethod
    def safe_provider_error(settings: BackendSettings, error: Exception, *, limit: int = 180) -> str:
        message = str(error)
        if settings.openrouter_api_key:
            token = settings.openrouter_api_key.get_secret_value()
            if token:
                message = message.replace(token, "[redacted]")
        return f"{error.__class__.__name__}: {message[:limit]}"

    @staticmethod
    def raw_response_excerpt(error: Exception) -> str | None:
        value: Any = getattr(error, "raw_response_excerpt", None)
        return str(value) if value else None

safe_provider_error = DraftProviderErrorUtilsComponent.safe_provider_error
raw_response_excerpt = DraftProviderErrorUtilsComponent.raw_response_excerpt


__all__ = (
    'safe_provider_error',
    'raw_response_excerpt',
    'DraftProviderErrorUtilsComponent',
)
