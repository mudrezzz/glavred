from pathlib import Path

import pytest
from pydantic import SecretStr, ValidationError

from backend.app.settings import BackendSettings


def test_settings_reads_openrouter_key_from_file(tmp_path: Path) -> None:
    secret_path = tmp_path / "openrouter"
    secret_path.write_text("remote-token\n", encoding="utf-8")

    settings = BackendSettings(
        _env_file=None,
        OPENROUTER_API_KEY="",
        OPENROUTER_API_KEY_FILE=secret_path,
    )

    assert settings.openrouter_api_key == SecretStr("remote-token")
    assert settings.has_openrouter_api_key is True


def test_explicit_openrouter_key_takes_precedence_over_file(tmp_path: Path) -> None:
    secret_path = tmp_path / "openrouter"
    secret_path.write_text("file-token", encoding="utf-8")

    settings = BackendSettings(
        _env_file=None,
        OPENROUTER_API_KEY="environment-token",
        OPENROUTER_API_KEY_FILE=secret_path,
    )

    assert settings.openrouter_api_key == SecretStr("environment-token")


def test_settings_reads_dev_auth_password_from_file(tmp_path: Path) -> None:
    secret_path = tmp_path / "password"
    secret_path.write_text("remote-password", encoding="utf-8")

    settings = BackendSettings(
        _env_file=None,
        GLAVRED_DEV_AUTH_PASSWORD="ignored-default",
        GLAVRED_DEV_AUTH_PASSWORD_FILE=secret_path,
    )

    assert settings.glavred_dev_auth_password == SecretStr("remote-password")


def test_missing_configured_secret_file_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValidationError, match="OPENROUTER_API_KEY_FILE is not readable"):
        BackendSettings(
            _env_file=None,
            OPENROUTER_API_KEY="",
            OPENROUTER_API_KEY_FILE=tmp_path / "missing",
        )
