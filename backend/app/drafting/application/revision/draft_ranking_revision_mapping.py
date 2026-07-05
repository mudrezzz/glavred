"""Owner: drafting.application.revision

Used by: DraftRun revision package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from datetime import UTC, datetime
from typing import Any

from backend.app.domain.draft_generation import DraftGenerationRequest, GeneratedDraft


def candidate_by_id(draft_artifact: dict[str, Any], candidate_id: str | None) -> dict[str, Any] | None:
    for candidate in draft_artifact.get("candidates", []):
        if isinstance(candidate, dict) and candidate.get("id") == candidate_id:
            return candidate
    return None


def candidate_to_draft(request: DraftGenerationRequest, candidate: dict[str, Any]) -> GeneratedDraft:
    return GeneratedDraft(
        id=f"draft-{request.brief.id}",
        brief_id=request.brief.id,
        title=str(candidate.get("title") or request.brief.title),
        body=str(candidate.get("body") or ""),
        version=1,
        status="draft",
        updated_at=datetime.now(UTC).isoformat(),
    )


def last_revised(loop_payload: dict[str, Any]) -> dict[str, Any] | None:
    for cycle in reversed(loop_payload.get("cycles", [])):
        if isinstance(cycle, dict) and isinstance(cycle.get("revisedCandidate"), dict):
            return cycle["revisedCandidate"]
    return None


def final_reason(source: str, ranking_reason: str, stop_reason: str) -> str:
    if source == "revisionLoop":
        return f"Accepted best candidate from revision loop. Stop reason: {stop_reason}."
    return f"Kept original ranked candidate. Ranking: {ranking_reason}. Stop reason: {stop_reason}."


def last(values: list[str]) -> str | None:
    return values[-1] if values else None


def safe_error(error: Exception) -> str:
    return f"{error.__class__.__name__}: {' '.join(str(error).split())[:240]}"


class DraftRankingRevisionMapping:
    """Owns mapping helpers between ranking/revision payloads and draft DTOs."""

    candidate_by_id = staticmethod(candidate_by_id)
    candidate_to_draft = staticmethod(candidate_to_draft)
    last_revised = staticmethod(last_revised)
    final_reason = staticmethod(final_reason)
    last = staticmethod(last)
    safe_error = staticmethod(safe_error)
