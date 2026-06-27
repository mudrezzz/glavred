from backend.app.settings import BackendSettings


def revision_iteration_limit(settings: BackendSettings) -> int:
    configured = max(1, int(settings.draft_revision_max_iterations or 1))
    return min(configured, 1) if settings.draft_run_execution_mode.strip() == "smoke" else configured
