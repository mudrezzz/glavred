from functools import lru_cache

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

    @property
    def has_openrouter_api_key(self) -> bool:
        if self.openrouter_api_key is None:
            return False
        return bool(self.openrouter_api_key.get_secret_value().strip())

    @property
    def has_openrouter_default_model(self) -> bool:
        return bool(self.openrouter_default_model.strip())


@lru_cache
def get_settings() -> BackendSettings:
    return BackendSettings()
