"""Owner: drafting.application.context

Used by: operation-specific provider dossier factories.
Does not own: provider-input policy, budgets, prompt construction, provider calls, or persistence.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from typing import Any, Mapping

from backend.app.domain.draft_run import DraftRun
from backend.app.drafting.application.context.contract_evidence_context_reader import ContractEvidenceContextReader
from backend.app.drafting.application.context.draft_run_artifact_index import DraftRunArtifactIndex
from backend.app.drafting.application.context.draft_run_handle_resolver import DraftRunHandleResolver
from backend.app.drafting.application.context.editorial_context_reader import EditorialContextReader
from backend.app.drafting.domain.provider_dossier import ArtifactHandle, ContextSelection, HandleResolution


class DraftRunContextAccessService:
    """Provides deterministic compact reads without provider or persistence side effects."""

    def __init__(self, index: DraftRunArtifactIndex) -> None:
        self._index = index
        self._contract_evidence = ContractEvidenceContextReader(index)
        self._editorial = EditorialContextReader(index)
        self._resolver = DraftRunHandleResolver(index)

    @classmethod
    def from_run(cls, run: DraftRun) -> DraftRunContextAccessService:
        return cls(DraftRunArtifactIndex.from_run(run))

    @classmethod
    def from_snapshot(cls, snapshot: Mapping[str, Any]) -> DraftRunContextAccessService:
        return cls(DraftRunArtifactIndex.from_snapshot(snapshot))

    @property
    def run_id(self) -> str:
        return self._index.run_id

    def post_contract(self) -> ContextSelection:
        return self._contract_evidence.post_contract()

    def evidence(self, limit: int = 12) -> ContextSelection:
        return self._contract_evidence.evidence(limit)

    def claims(self, limit: int = 12) -> ContextSelection:
        return self._contract_evidence.claims(limit)

    def rules(self, limit: int = 16) -> ContextSelection:
        return self._contract_evidence.rules(limit)

    def planning(self) -> ContextSelection:
        return self._editorial.planning()

    def rhetorical_plan(self, plan_id: str | None) -> ContextSelection:
        return self._editorial.rhetorical_plan(plan_id)

    def candidate_summaries(self, limit: int = 4) -> ContextSelection:
        return self._editorial.candidate_summaries(limit)

    def selected_candidate(self, candidate_id: str | None) -> ContextSelection:
        return self._editorial.selected_candidate(candidate_id)

    def validation_issues(self, candidate_id: str | None = None, limit: int = 20) -> ContextSelection:
        return self._editorial.validation_issues(candidate_id, limit)

    def final_quality_lifecycle(self, limit: int = 20) -> ContextSelection:
        return self._editorial.final_quality_lifecycle(limit)

    def repair_history(self) -> ContextSelection:
        return self._editorial.repair_history()

    def resolve(self, handle: ArtifactHandle) -> HandleResolution:
        return self._resolver.resolve(handle)


__all__ = ("DraftRunContextAccessService",)
