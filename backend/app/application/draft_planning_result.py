from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DraftPlanningStepResult:
    artifact_payload: dict[str, Any]
    ai_run_id: str | None
