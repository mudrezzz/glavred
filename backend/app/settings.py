from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class BackendSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = Field(default="local", validation_alias="GLAVRED_ENV")
    api_host: str = Field(default="127.0.0.1", validation_alias="GLAVRED_API_HOST")
    api_port: int = Field(default=8000, validation_alias="GLAVRED_API_PORT")
    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        validation_alias="GLAVRED_CORS_ORIGINS",
    )
    ai_run_audit_db_path: Path = Field(
        default=Path("var/glavred-ai-runs.sqlite3"),
        validation_alias="AI_RUN_AUDIT_DB_PATH",
    )
    draft_run_db_path: Path = Field(
        default=Path("var/glavred-draft-runs.sqlite3"),
        validation_alias="DRAFT_RUN_DB_PATH",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")

    openrouter_api_key: SecretStr | None = Field(
        default=None,
        validation_alias="OPENROUTER_API_KEY",
    )
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        validation_alias="OPENROUTER_BASE_URL",
    )
    openrouter_default_model: str = Field(
        default="",
        validation_alias="OPENROUTER_DEFAULT_MODEL",
    )
    openrouter_app_name: str = Field(default="Glavred", validation_alias="OPENROUTER_APP_NAME")
    openrouter_http_referer: str = Field(
        default="http://localhost:5173",
        validation_alias="OPENROUTER_HTTP_REFERER",
    )
    openrouter_web_tools_enabled: bool = Field(
        default=False,
        validation_alias="OPENROUTER_WEB_TOOLS_ENABLED",
    )
    openrouter_web_search_model: str = Field(
        default="",
        validation_alias="OPENROUTER_WEB_SEARCH_MODEL",
    )
    openrouter_web_search_max_results: int = Field(
        default=5,
        validation_alias="OPENROUTER_WEB_SEARCH_MAX_RESULTS",
    )

    @property
    def has_openrouter_api_key(self) -> bool:
        if self.openrouter_api_key is None:
            return False
        return bool(self.openrouter_api_key.get_secret_value().strip())

    @property
    def has_openrouter_default_model(self) -> bool:
        return bool(self.openrouter_default_model.strip())

    @property
    def openrouter_web_search_model_or_default(self) -> str:
        return self.openrouter_web_search_model.strip() or self.openrouter_default_model

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> BackendSettings:
    return BackendSettings()
