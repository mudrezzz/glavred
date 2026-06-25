from backend.app.settings import BackendSettings


def revision_iteration_limit(settings: BackendSettings) -> int:
    return max(1, int(settings.draft_revision_max_iterations or 1))
