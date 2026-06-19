from backend.app.application.deterministic_draft_service import DeterministicDraftService
from backend.app.application.draft_run_pipeline import DraftRunPipeline
from backend.app.infrastructure.celery_app import celery_app
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.app.settings import get_settings


@celery_app.task(name="glavred.draft_runs.execute")
def execute_draft_run(run_id: str) -> str:
    settings = get_settings()
    repository = SqliteDraftRunRepository(settings.draft_run_db_path)
    pipeline = DraftRunPipeline(
        repository=repository,
        deterministic_draft_service=DeterministicDraftService(),
    )
    pipeline.execute(run_id)
    return run_id
