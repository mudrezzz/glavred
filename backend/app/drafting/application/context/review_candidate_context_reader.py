"""Owner: drafting.application.context

Used by: review, ranking, revision, and final-quality candidate dossier reads.
Does not own: validation findings, provider calls, prompt construction, or selection decisions.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from backend.app.drafting.application.context.candidate_review_projection import CandidateReviewProjectionBuilder
from backend.app.drafting.application.context.draft_run_artifact_index import DraftRunArtifactIndex
from backend.app.drafting.domain.provider_dossier import ArtifactHandle, ContextSelection


class ReviewCandidateContextReader:
    def __init__(self, index: DraftRunArtifactIndex) -> None:
        self._index = index
        self._projections = CandidateReviewProjectionBuilder()

    def candidate_summaries(self, limit: int = 4) -> ContextSelection:
        all_records = self._candidate_records(include_revisions=False)
        records = all_records[: max(0, limit)]
        return ContextSelection(
            "candidates",
            [self._projections.build(candidate) for candidate, _ in records],
            tuple(handle for _, handle in records),
            available=bool(records),
            total_count=len(all_records),
            selected_count=len(records),
            trimmed_count=max(0, len(all_records) - len(records)),
        )

    def selected_candidate(self, candidate_id: str | None) -> ContextSelection:
        match = next(
            (
                (candidate, handle)
                for candidate, handle in self._candidate_records(include_revisions=True)
                if str(candidate.get("id")) == str(candidate_id)
            ),
            None,
        )
        if match is None:
            return ContextSelection("candidate", None, available=False)
        candidate, handle = match
        value = self._select(
            candidate,
            ("id", "title", "body", "rhetoricalPlanId", "usedEvidence", "ruleCoverage", "risks", "weaknesses"),
        )
        return ContextSelection("candidate", value, (handle,), total_count=1, selected_count=1)

    def _candidate_records(self, *, include_revisions: bool) -> list[tuple[dict[str, Any], ArtifactHandle]]:
        records: list[tuple[dict[str, Any], ArtifactHandle]] = []
        checkpoint = self._mapping(self._mapping(self._index.step_payload("validation")).get("reviewContext"))
        checkpoint_candidates = self._records(checkpoint.get("candidates"))
        for index, candidate in enumerate(checkpoint_candidates):
            records.append((candidate, self._handle(("reviewContext", "candidates", index), candidate, index)))
        current = self._mapping(checkpoint.get("currentCandidate"))
        if current:
            records.append((current, self._handle(("reviewContext", "currentCandidate"), current, "current")))
        if not checkpoint_candidates:
            self._append_initial_candidates(records)
            if include_revisions:
                self._append_revision_candidates(records)
        deduped: dict[str, tuple[dict[str, Any], ArtifactHandle]] = {}
        for candidate, handle in records:
            deduped[str(candidate.get("id") or handle.id)] = (candidate, handle)
        return list(deduped.values())

    def _append_initial_candidates(self, records: list[tuple[dict[str, Any], ArtifactHandle]]) -> None:
        draft = self._mapping(self._index.step_payload("draft"))
        for index, candidate in enumerate(self._records(draft.get("candidates"))):
            records.append((candidate, self._draft_handle(("candidates", index), candidate, index)))
        tournament = self._mapping(self._mapping(self._index.step_payload("validation")).get("alternativeAngleTournament"))
        challenger = self._mapping(tournament.get("candidate"))
        if challenger:
            records.append((challenger, self._handle(("alternativeAngleTournament", "candidate"), challenger, "challenger")))

    def _append_revision_candidates(self, records: list[tuple[dict[str, Any], ArtifactHandle]]) -> None:
        ranking = self._ranking_revision()
        revised = self._mapping(ranking.get("revisedCandidate"))
        if revised:
            records.append((revised, self._handle(("rankingRevision", "revisedCandidate"), revised, "revised")))
        loop = self._mapping(ranking.get("revisionLoop"))
        for index, cycle in enumerate(self._records(loop.get("cycles"))):
            candidate = self._mapping(cycle.get("revisedCandidate"))
            if candidate:
                records.append((candidate, self._handle(("rankingRevision", "revisionLoop", "cycles", index, "revisedCandidate"), candidate, index)))
        gate = self._mapping(ranking.get("finalQualityGate"))
        for index, cycle in enumerate(self._records(gate.get("repairCycles"))):
            candidate = self._mapping(cycle.get("revisedCandidate"))
            if candidate:
                records.append((candidate, self._handle(("rankingRevision", "finalQualityGate", "repairCycles", index, "revisedCandidate"), candidate, index)))

    def _ranking_revision(self) -> Mapping[str, Any]:
        validation = self._mapping(self._index.step_payload("validation"))
        return self._mapping(validation.get("rankingRevision"))

    def _handle(self, path: tuple[str | int, ...], candidate: Mapping[str, Any], fallback: Any) -> ArtifactHandle:
        return ArtifactHandle.create(
            run_id=self._index.run_id,
            step_key="validation",
            artifact_type="candidate",
            artifact_id=str(candidate.get("id") or fallback),
            path=path,
        )

    def _draft_handle(self, path: tuple[str | int, ...], candidate: Mapping[str, Any], fallback: Any) -> ArtifactHandle:
        return ArtifactHandle.create(
            run_id=self._index.run_id,
            step_key="draft",
            artifact_type="candidate",
            artifact_id=str(candidate.get("id") or fallback),
            path=path,
        )

    def _mapping(self, value: Any) -> Mapping[str, Any]:
        return value if isinstance(value, Mapping) else {}

    def _records(self, value: Any) -> list[dict[str, Any]]:
        return [dict(item) for item in value if isinstance(item, Mapping)] if isinstance(value, list) else []

    def _select(self, value: Mapping[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
        return {key: value.get(key) for key in keys if value.get(key) not in (None, [], {})}


__all__ = ("ReviewCandidateContextReader",)
