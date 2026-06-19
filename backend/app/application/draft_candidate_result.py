from dataclasses import dataclass
from typing import Any

from backend.app.domain.draft_generation import GeneratedDraft


@dataclass(frozen=True)
class DraftCandidateGenerationResult:
    artifact_payload: dict[str, Any]
    final_draft: GeneratedDraft
    ai_run_ids: list[str]
