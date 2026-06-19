from backend.app.infrastructure.celery_app import celery_app
from backend.app.infrastructure.draft_run_pipeline_factory import build_draft_run_pipeline
from backend.app.settings import get_settings


@celery_app.task(name="glavred.draft_runs.execute")
def execute_draft_run(run_id: str) -> str:
    settings = get_settings()
    build_draft_run_pipeline(settings).execute(run_id)
    return run_id
