from backend.app.application.draft_run_service import DraftRunDispatcher
from backend.app.infrastructure.draft_run_tasks import execute_draft_run


class CeleryDraftRunDispatcher(DraftRunDispatcher):
    def dispatch(self, run_id: str) -> None:
        execute_draft_run.delay(run_id)
