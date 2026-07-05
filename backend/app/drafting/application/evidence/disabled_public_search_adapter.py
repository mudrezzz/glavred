"""Owner: drafting.application.evidence

Used by: DraftRun evidence migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from backend.app.drafting.application.evidence.public_evidence_ports import PublicEvidenceSearchResult, PublicEvidenceSearchTask
from backend.app.domain.draft_public_evidence import PublicEvidenceAttempt, PublicEvidenceAttemptStatus


class DisabledPublicSearchAdapter:
    def search(self, task: PublicEvidenceSearchTask) -> PublicEvidenceSearchResult:
        return PublicEvidenceSearchResult(
            attempts=[PublicEvidenceAttempt(
                id=_attempt_id("search", task.task_id, task.source_intent_item_id),
                task_id=task.task_id,
                source_intent_item_id=task.source_intent_item_id,
                kind="search",
                target=task.technical_target or task.query,
                status=PublicEvidenceAttemptStatus.NOT_CONFIGURED,
                notes=["Search provider is not configured; this planned task is not evidence."],
                metadata=_task_metadata(task),
            )],
            metadata={"searchProvider": "notConfigured"},
        )


def _attempt_id(prefix: str, task_id: str | None, source_intent_item_id: str | None) -> str:
    suffix = task_id or source_intent_item_id or "unlinked"
    return f"{prefix}-{suffix}"


def _task_metadata(task: PublicEvidenceSearchTask) -> dict:
    return {
        "builtQuery": task.query,
        "originalTask": task.original_task,
        "sourceTarget": task.source_target,
        "exclusions": task.exclusions,
    }


__all__ = (
    'DisabledPublicSearchAdapter',
)
