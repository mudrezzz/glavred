"""Owner: drafting.application.context

Used by: provider dossier trace and replay diagnostics.
Does not own: provider payload selection, persistence, or user-facing trace rendering.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from backend.app.drafting.application.context.draft_run_artifact_index import DraftRunArtifactIndex
from backend.app.drafting.domain.provider_dossier import (
    ArtifactHandle,
    HandleResolution,
    HandleResolutionStatus,
)


class DraftRunHandleResolver:
    def __init__(self, index: DraftRunArtifactIndex) -> None:
        self._index = index

    def resolve(self, handle: ArtifactHandle) -> HandleResolution:
        if handle.run_id != self._index.run_id:
            return HandleResolution(
                HandleResolutionStatus.RUN_MISMATCH,
                handle,
                reason="handle-run-does-not-match-current-run",
            )
        value = self._index.value_at(handle.step_key, handle.path)
        if value is None:
            return HandleResolution(
                HandleResolutionStatus.NOT_FOUND,
                handle,
                reason="artifact-path-not-found",
            )
        if self._artifact_id(value) != handle.artifact_id:
            return HandleResolution(
                HandleResolutionStatus.STALE,
                handle,
                reason="artifact-identity-changed",
            )
        return HandleResolution(HandleResolutionStatus.RESOLVED, handle, value=value)

    def _artifact_id(self, value: Any) -> str:
        if isinstance(value, Mapping):
            if value.get("id"):
                return str(value["id"])
            if value.get("candidateId") and value.get("validatorId"):
                return f"{value['candidateId']}:{value['validatorId']}"
            for key in ("validatorId", "candidateId"):
                if value.get(key):
                    return str(value[key])
        return "artifact"


__all__ = ("DraftRunHandleResolver",)
