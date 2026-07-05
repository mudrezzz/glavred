"""Owner: drafting.application.planning

Used by: DraftRun planning migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DraftPlanningStepResult:
    artifact_payload: dict[str, Any]
    ai_run_id: str | None
    ai_run_ids: list[str] | None = None


__all__ = (
    'DraftPlanningStepResult',
    'DraftPlanningStepResultDTO',
)
