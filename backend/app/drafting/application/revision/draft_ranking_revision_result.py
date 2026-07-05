"""Owner: drafting.application.revision

Used by: DraftRun revision package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from dataclasses import dataclass
from typing import Any

from backend.app.domain.draft_generation import GeneratedDraft


@dataclass(frozen=True)
class DraftRankingRevisionResult:
    artifact_payload: dict[str, Any]
    final_draft: GeneratedDraft | None
    ai_run_ids: list[str]
