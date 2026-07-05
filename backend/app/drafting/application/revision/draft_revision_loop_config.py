"""Owner: drafting.application.revision

Used by: DraftRun revision package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from backend.app.settings import BackendSettings


def revision_iteration_limit(settings: BackendSettings) -> int:
    configured = max(1, int(settings.draft_revision_max_iterations or 1))
    return min(configured, 1) if settings.draft_run_execution_mode.strip() == "smoke" else configured
