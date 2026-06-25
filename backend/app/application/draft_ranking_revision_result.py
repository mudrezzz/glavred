from dataclasses import dataclass
from typing import Any

from backend.app.domain.draft_generation import GeneratedDraft


@dataclass(frozen=True)
class DraftRankingRevisionResult:
    artifact_payload: dict[str, Any]
    final_draft: GeneratedDraft | None
    ai_run_ids: list[str]
