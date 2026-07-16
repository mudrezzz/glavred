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
    cors_origins: str = Field(default="http://localhost:5173,http://127.0.0.1:5173", validation_alias="GLAVRED_CORS_ORIGINS")
    ai_run_audit_db_path: Path = Field(default=Path("var/glavred-ai-runs.sqlite3"), validation_alias="AI_RUN_AUDIT_DB_PATH")
    draft_run_db_path: Path = Field(default=Path("var/glavred-draft-runs.sqlite3"), validation_alias="DRAFT_RUN_DB_PATH")
    portfolio_db_path: Path = Field(default=Path("var/glavred-portfolio.sqlite3"), validation_alias="PORTFOLIO_DB_PATH")
    glavred_auth_mode: str = Field(default="dev-password", validation_alias="GLAVRED_AUTH_MODE")
    glavred_dev_auth_password: SecretStr = Field(default=SecretStr("glavred-demo"), validation_alias="GLAVRED_DEV_AUTH_PASSWORD")
    glavred_session_cookie_name: str = Field(default="glavred_session", validation_alias="GLAVRED_SESSION_COOKIE_NAME")
    glavred_session_ttl_hours: int = Field(default=168, validation_alias="GLAVRED_SESSION_TTL_HOURS")
    draft_revision_max_iterations: int = Field(default=3, validation_alias="DRAFT_REVISION_MAX_ITERATIONS")
    draft_run_execution_mode: str = Field(default="standard", validation_alias="DRAFT_RUN_EXECUTION_MODE")
    draft_research_budget_overrides: str = Field(default="", validation_alias="DRAFT_RESEARCH_BUDGET_OVERRIDES")
    draft_run_smoke_budget_overrides: str = Field(default="", validation_alias="DRAFT_RUN_SMOKE_BUDGET_OVERRIDES")
    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")

    openrouter_api_key: SecretStr | None = Field(default=None, validation_alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1", validation_alias="OPENROUTER_BASE_URL")
    openrouter_default_model: str = Field(default="", validation_alias="OPENROUTER_DEFAULT_MODEL")
    openrouter_backup_model: str = Field(default="", validation_alias="OPENROUTER_BACKUP_MODEL")
    draft_research_model: str = Field(default="", validation_alias="DRAFT_RESEARCH_MODEL")
    draft_strategy_model: str = Field(default="", validation_alias="DRAFT_STRATEGY_MODEL")
    draft_writer_model: str = Field(default="", validation_alias="DRAFT_WRITER_MODEL")
    draft_critic_model: str = Field(default="", validation_alias="DRAFT_CRITIC_MODEL")
    draft_review_model: str = Field(default="", validation_alias="DRAFT_REVIEW_MODEL")
    draft_another_angle_model: str = Field(default="", validation_alias="DRAFT_ANOTHER_ANGLE_MODEL")
    draft_final_gate_model: str = Field(default="", validation_alias="DRAFT_FINAL_GATE_MODEL")
    draft_final_repair_max_iterations: int = Field(default=2, validation_alias="DRAFT_FINAL_REPAIR_MAX_ITERATIONS")
    draft_evidence_interpretation_timeout_seconds: float = Field(default=75, validation_alias="DRAFT_EVIDENCE_INTERPRETATION_TIMEOUT_SECONDS")
    draft_writer_temperature: str = Field(default="0.65", validation_alias="DRAFT_WRITER_TEMPERATURE")
    draft_writer_top_p: str = Field(default="0.9", validation_alias="DRAFT_WRITER_TOP_P")
    draft_revision_temperature: str = Field(default="0.35", validation_alias="DRAFT_REVISION_TEMPERATURE")
    draft_revision_top_p: str = Field(default="0.85", validation_alias="DRAFT_REVISION_TOP_P")
    draft_json_repair_temperature: str = Field(default="0.15", validation_alias="DRAFT_JSON_REPAIR_TEMPERATURE")
    draft_another_angle_temperature: str = Field(default="0.8", validation_alias="DRAFT_ANOTHER_ANGLE_TEMPERATURE")
    openrouter_app_name: str = Field(default="Glavred", validation_alias="OPENROUTER_APP_NAME")
    openrouter_http_referer: str = Field(default="http://localhost:5173", validation_alias="OPENROUTER_HTTP_REFERER")
    openrouter_web_tools_enabled: bool = Field(default=False, validation_alias="OPENROUTER_WEB_TOOLS_ENABLED")
    openrouter_web_search_model: str = Field(default="", validation_alias="OPENROUTER_WEB_SEARCH_MODEL")
    openrouter_web_search_max_results: int = Field(default=5, validation_alias="OPENROUTER_WEB_SEARCH_MAX_RESULTS")
    upstream_signal_extraction_model: str = Field(default="", validation_alias="UPSTREAM_SIGNAL_EXTRACTION_MODEL")

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
    def openrouter_backup_model_or_none(self) -> str | None:
        value = self.openrouter_backup_model.strip()
        return value or None

    @property
    def upstream_signal_extraction_model_or_default(self) -> str:
        return (
            self.upstream_signal_extraction_model.strip()
            or self.draft_review_model.strip()
            or self.openrouter_default_model.strip()
        )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> BackendSettings:
    return BackendSettings()
