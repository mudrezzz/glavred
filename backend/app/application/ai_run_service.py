from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import uuid4

from backend.app.domain.ai_run import AiRun, AiRunCapability, AiRunProvider, AiRunStatus

SENSITIVE_KEY_PARTS = ("api_key", "apikey", "secret", "password", "authorization")
SENSITIVE_TOKEN_KEYS = {"token", "access_token", "refresh_token", "auth_token", "bearer_token"}


class AiRunRepository(Protocol):
    def save(self, run: AiRun) -> AiRun: ...
    def get(self, run_id: str) -> AiRun | None: ...
    def list(self, *, limit: int, capability: AiRunCapability | None = None) -> list[AiRun]: ...


class AiRunService:
    def __init__(self, repository: AiRunRepository) -> None:
        self._repository = repository

    def create_recorded_run(self, *, capability: AiRunCapability, provider: AiRunProvider,
                            model: str | None, request_payload: dict[str, Any]) -> AiRun:
        return self._create_run(
            capability=capability, provider=provider, model=model, request_payload=request_payload,
            status=AiRunStatus.RECORDED, result_payload=None, error=None, fallback_used=False,
        )

    def create_completed_run(
        self,
        *,
        capability: AiRunCapability,
        provider: AiRunProvider,
        model: str | None,
        request_payload: dict[str, Any],
        result_payload: dict[str, Any],
        fallback_used: bool,
        error: str | None = None,
    ) -> AiRun:
        return self._create_run(
            capability=capability, provider=provider, model=model, request_payload=request_payload,
            status=AiRunStatus.SUCCEEDED, result_payload=result_payload, error=error, fallback_used=fallback_used,
        )

    def create_failed_run(self, *, capability: AiRunCapability, provider: AiRunProvider,
                          model: str | None, request_payload: dict[str, Any], error: str,
                          result_payload: dict[str, Any] | None = None) -> AiRun:
        return self._create_run(
            capability=capability, provider=provider, model=model, request_payload=request_payload,
            status=AiRunStatus.FAILED, result_payload=result_payload, error=error, fallback_used=False,
        )

    def get_run(self, run_id: str) -> AiRun | None:
        return self._repository.get(run_id)

    def list_runs(
        self,
        *,
        limit: int = 20,
        capability: AiRunCapability | None = None,
    ) -> list[AiRun]:
        normalized_limit = min(max(limit, 1), 100)
        return self._repository.list(limit=normalized_limit, capability=capability)

    def _create_run(
        self, *, capability: AiRunCapability, provider: AiRunProvider, model: str | None,
        request_payload: dict[str, Any], status: AiRunStatus, result_payload: dict[str, Any] | None,
        error: str | None, fallback_used: bool,
    ) -> AiRun:
        now = datetime.now(UTC)
        return self._repository.save(AiRun(
            id=str(uuid4()), capability=capability, status=status, provider=provider, model=model,
            request_payload=self._redact_sensitive_values(request_payload),
            result_payload=self._redact_sensitive_values(result_payload) if result_payload is not None else None,
            error=error, fallback_used=fallback_used, created_at=now, updated_at=now,
        ))

    def _redact_sensitive_values(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: "[redacted]" if self._is_sensitive_key(key) else self._redact_sensitive_values(item)
                for key, item in value.items()
            }

        if isinstance(value, list):
            return [self._redact_sensitive_values(item) for item in value]

        return value

    def _is_sensitive_key(self, key: str) -> bool:
        normalized = key.lower().replace("-", "_")
        return normalized in SENSITIVE_TOKEN_KEYS or normalized.endswith("token") or any(
            part in normalized for part in SENSITIVE_KEY_PARTS
        )
