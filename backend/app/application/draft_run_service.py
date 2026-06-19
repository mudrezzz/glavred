from typing import Protocol

from backend.app.application.draft_run_payloads import (
    input_summary_from_request,
    request_to_payload,
)
from backend.app.domain.draft_generation import DraftGenerationRequest
from backend.app.domain.draft_run import DraftRun, DraftRunStatus, create_queued_draft_run
from backend.app.domain.draft_run_context import DraftRunContext


class DraftRunRepository(Protocol):
    def save(self, run: DraftRun) -> DraftRun: ...

    def get(self, run_id: str) -> DraftRun | None: ...

    def set_run_status(
        self,
        run_id: str,
        status: DraftRunStatus,
        *,
        error: str | None = None,
        final_draft: dict | None = None,
        ai_run_ids: list[str] | None = None,
    ) -> None: ...


class DraftRunDispatcher(Protocol):
    def dispatch(self, run_id: str) -> None: ...


class DraftRunService:
    def __init__(self, repository: DraftRunRepository, dispatcher: DraftRunDispatcher) -> None:
        self._repository = repository
        self._dispatcher = dispatcher

    def create_run(
        self,
        request: DraftGenerationRequest,
        draft_context: DraftRunContext | None = None,
    ) -> DraftRun:
        run = create_queued_draft_run(
            request_payload=request_to_payload(request, draft_context),
            input_summary=input_summary_from_request(request, draft_context),
        )
        self._repository.save(run)
        try:
            self._dispatcher.dispatch(run.id)
        except Exception as exc:  # pragma: no cover - defensive infrastructure boundary
            safe_error = str(exc)[:500] or "Failed to dispatch draft run"
            self._repository.set_run_status(run.id, DraftRunStatus.FAILED, error=safe_error)
            loaded = self._repository.get(run.id)
            return loaded or run
        loaded = self._repository.get(run.id)
        return loaded or run

    def get_run(self, run_id: str) -> DraftRun | None:
        return self._repository.get(run_id)
