"""Apply file-backed runtime secrets to typed backend settings.

Owner: shared backend runtime configuration.
Used by: backend settings initialization.
Does not own: secret transport, provider calls, or container mounts.
Architecture doc: docs/adr/2026-07-22-use-isolated-remote-docker-for-test-runtime.md.
"""

from pathlib import Path
from typing import Protocol

from pydantic import SecretStr


class FileBackedSettings(Protocol):
    glavred_dev_auth_password: SecretStr
    glavred_dev_auth_password_file: Path | None
    openrouter_api_key: SecretStr | None
    openrouter_api_key_file: Path | None


def apply_file_backed_secrets(settings: FileBackedSettings) -> None:
    if settings.glavred_dev_auth_password_file is not None:
        settings.glavred_dev_auth_password = SecretStr(
            read_required_secret(settings.glavred_dev_auth_password_file, "GLAVRED_DEV_AUTH_PASSWORD_FILE")
        )
    if settings.openrouter_api_key_file is not None and not _has_secret(settings.openrouter_api_key):
        settings.openrouter_api_key = SecretStr(
            read_required_secret(settings.openrouter_api_key_file, "OPENROUTER_API_KEY_FILE")
        )


def read_required_secret(path: Path, setting_name: str) -> str:
    try:
        value = path.read_text(encoding="utf-8").strip()
    except OSError as error:
        raise ValueError(f"{setting_name} is not readable: {path}") from error
    if not value:
        raise ValueError(f"{setting_name} is empty")
    return value


def _has_secret(secret: SecretStr | None) -> bool:
    return secret is not None and bool(secret.get_secret_value().strip())
