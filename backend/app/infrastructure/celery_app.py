from celery import Celery

from backend.app.settings import get_settings


def create_celery_app() -> Celery:
    settings = get_settings()
    app = Celery(
        "glavred_backend",
        broker=settings.redis_url,
        backend=settings.redis_url,
        include=["backend.app.infrastructure.draft_run_tasks"],
    )
    app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        task_track_started=True,
        task_soft_time_limit=900,
        task_time_limit=960,
    )
    return app


celery_app = create_celery_app()
