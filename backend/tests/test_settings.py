from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings


def test_settings_defaults_without_env_file() -> None:
    settings = BackendSettings(
        _env_file=None,
        OPENROUTER_API_KEY="",
        OPENROUTER_DEFAULT_MODEL="",
    )

    assert settings.environment == "local"
    assert settings.api_host == "127.0.0.1"
    assert settings.api_port == 8000
    assert settings.cors_origin_list == ["http://localhost:5173", "http://127.0.0.1:5173"]
    assert settings.openrouter_base_url == "https://openrouter.ai/api/v1"
    assert settings.has_openrouter_api_key is False
    assert settings.has_openrouter_default_model is False
    assert settings.openrouter_web_tools_enabled is False
    assert settings.openrouter_web_search_max_results == 5


def test_openrouter_config_is_unconfigured_without_token_or_model() -> None:
    settings = BackendSettings(
        _env_file=None,
        OPENROUTER_API_KEY="",
        OPENROUTER_DEFAULT_MODEL="",
    )

    status = OpenRouterConfigValidator().evaluate(settings)

    assert status.configured is False
    assert status.default_model_configured is False
    assert status.base_url == "https://openrouter.ai/api/v1"


def test_openrouter_config_is_configured_with_token_and_model() -> None:
    settings = BackendSettings(
        _env_file=None,
        OPENROUTER_API_KEY="test-token",
        OPENROUTER_DEFAULT_MODEL="openrouter/test-model",
    )

    status = OpenRouterConfigValidator().evaluate(settings)

    assert status.configured is True
    assert status.default_model_configured is True
    assert settings.openrouter_web_search_model_or_default == "openrouter/test-model"
