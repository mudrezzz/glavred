from typing import Any, Protocol

from backend.app.domain.draft_run import DraftRun
from backend.app.domain.draft_run_steps import DraftRunStepKey


class ProgressPayload(Protocol):
    def payload(self, status: str | None = None) -> dict[str, Any]: ...


def step_artifact(run: DraftRun | None, step_key: DraftRunStepKey) -> dict[str, Any]:
    if run is None:
        return {}
    for step in run.steps:
        if step.key == step_key and isinstance(step.artifact_payload, dict):
            return dict(step.artifact_payload)
    return {}


def with_progress(base: dict[str, Any], progress_payload: dict[str, Any]) -> dict[str, Any]:
    return {**base, "progress": progress_payload}


def with_progress_payload(artifact_payload: dict[str, Any], progress: ProgressPayload | None) -> dict[str, Any]:
    return artifact_payload if progress is None else with_progress(artifact_payload, progress.payload("succeeded"))
