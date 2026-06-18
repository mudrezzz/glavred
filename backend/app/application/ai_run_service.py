from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import uuid4

from backend.app.domain.ai_run import AiRun, AiRunCapability, AiRunProvider, AiRunStatus

SENSITIVE_KEY_PARTS = ("api_key", "apikey", "token", "secret", "password", "authorization")


class AiRunRepository(Protocol):
    def save(self, run: AiRun) -> AiRun: ...

    def get(self, run_id: str) -> AiRun | None: ...

    def list(self, *, limit: int, capability: AiRunCapability | None = None) -> list[AiRun]: ...


class AiRunService:
    def __init__(self, repository: AiRunRepository) -> None:
        self._repository = repository

    def create_recorded_run(
        self,
        *,
        capability: AiRunCapability,
        provider: AiRunProvider,
        model: str | None,
        request_payload: dict[str, Any],
    ) -> AiRun:
        now = datetime.now(UTC)
        run = AiRun(
            id=str(uuid4()),
            capability=capability,
            status=AiRunStatus.RECORDED,
            provider=provider,
            model=model,
            request_payload=self._redact_sensitive_values(request_payload),
            result_payload=None,
            error=None,
            fallback_used=False,
            created_at=now,
            updated_at=now,
        )
        return self._repository.save(run)

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
        return any(part in normalized for part in SENSITIVE_KEY_PARTS)
