from typing import Any

from backend.app.application.draft_article_dossier_builder import ArticleDossierBuilder
from backend.app.application.draft_context_pack_builder import ContextPackBuilder, context_pack_for_role
from backend.app.domain.draft_model_roles import DraftModelRole


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


def context_pack_from_payload(payload: dict[str, Any] | None, role: DraftModelRole) -> dict[str, Any] | None:
    return context_pack_for_role(payload, role)
