"""Owner: drafting.application.evidence

Used by: DraftRun evidence migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from dataclasses import dataclass, field
from typing import Any, Protocol

from backend.app.domain.draft_public_evidence import PublicEvidenceAttempt, PublicEvidenceItem, PublicEvidenceWarning


@dataclass(frozen=True)
class PublicUrlReadResult:
    url: str
    title: str
    text: str
    final_url: str | None = None


class PublicUrlReader(Protocol):
    def read(self, url: str) -> PublicUrlReadResult: ...


@dataclass(frozen=True)
class PublicEvidenceSearchResult:
    attempts: list[PublicEvidenceAttempt]
    items: list[PublicEvidenceItem] = field(default_factory=list)
    warnings: list[PublicEvidenceWarning] = field(default_factory=list)
    ai_run_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PublicEvidenceSearchTask:
    query: str
    task_id: str | None
    source_intent_item_id: str | None
    kind: str
    technical_target: str | None
    instruction: str
    source_target: dict[str, Any] | None = None
    exclusions: list[str] = field(default_factory=list)
    original_task: dict[str, Any] = field(default_factory=dict)
    max_results: int | None = None


class PublicSearchAdapter(Protocol):
    def search(self, task: PublicEvidenceSearchTask) -> PublicEvidenceSearchResult: ...


class DisabledPublicUrlReader:
    def read(self, url: str) -> PublicUrlReadResult:
        raise RuntimeError("Public URL reader is not configured")


__all__ = (
    'PublicUrlReadResult',
    'PublicUrlReader',
    'PublicEvidenceSearchResult',
    'PublicEvidenceSearchTask',
    'PublicSearchAdapter',
    'DisabledPublicUrlReader',
)
