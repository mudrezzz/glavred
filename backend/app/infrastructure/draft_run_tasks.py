from billiard.exceptions import SoftTimeLimitExceeded

from backend.app.infrastructure.celery_app import celery_app
from backend.app.infrastructure.draft_run_pipeline_factory import build_draft_run_pipeline
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.app.domain.draft_run import DraftRunStatus
from backend.app.settings import get_settings


@celery_app.task(name="glavred.draft_runs.execute")
def execute_draft_run(run_id: str) -> str:
    settings = get_settings()
    try:
        build_draft_run_pipeline(settings).execute(run_id)
    except SoftTimeLimitExceeded:
        SqliteDraftRunRepository(settings.draft_run_db_path).set_run_status(
            run_id,
            DraftRunStatus.FAILED,
            error="DraftRun worker exceeded soft time limit.",
        )
        raise
    return run_id
