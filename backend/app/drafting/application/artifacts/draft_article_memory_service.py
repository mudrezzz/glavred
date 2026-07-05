"""Owner: drafting.application.artifacts

Used by: DraftRun artifact migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.artifacts.draft_article_dossier_builder import ArticleDossierBuilder
from backend.app.drafting.application.artifacts.draft_context_pack_builder import ContextPackBuilder


class DraftArticleMemoryService:
    def __init__(
        self,
        *,
        dossier_builder: ArticleDossierBuilder | None = None,
        context_pack_builder: ContextPackBuilder | None = None,
    ) -> None:
        self._dossier_builder = dossier_builder or ArticleDossierBuilder()
        self._context_pack_builder = context_pack_builder or ContextPackBuilder()

    def attach(self, payload: dict[str, Any], **artifacts: dict[str, Any] | None) -> dict[str, Any]:
        memory = self.build(**artifacts)
        return {**payload, **memory}

    def build(self, **artifacts: dict[str, Any] | None) -> dict[str, Any]:
        dossier = self._dossier_builder.build(**artifacts)
        return {
            "articleDossier": dossier.to_payload(),
            "contextPacks": self._context_pack_builder.build_all(dossier),
        }

__all__ = (
    'DraftArticleMemoryService',
)
