"""Owner: drafting.application.generation

Used by: DraftRun generation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.generation.draft_candidate_publishability import DraftCandidatePublishabilityPolicy
from backend.app.domain.draft_candidates import DraftCandidateSelection, DraftCandidateScore


class DraftCandidateSelectionService:
    def __init__(self, publishability_policy: DraftCandidatePublishabilityPolicy | None = None) -> None:
        self._publishability_policy = publishability_policy or DraftCandidatePublishabilityPolicy()

    def select(self, candidates: list[dict[str, Any]]) -> DraftCandidateSelection:
        provider_alternative_exists = self._publishability_policy.has_publishable_provider_candidate(candidates)
        scores = [self._score(candidate, provider_alternative_exists=provider_alternative_exists) for candidate in candidates]
        eligible_scores = [score for score in scores if score.publishable and score.selection_status != "excluded"]
        if not eligible_scores:
            return DraftCandidateSelection(
                selected_candidate_id=None,
                reason="No publishable draft candidate passed the selection guard.",
                scorecard=scores,
                unresolved_risks=["draft-candidate-selection-blocked"],
            )
        selected = max(eligible_scores, key=lambda score: (score.total, score.evidence_grounding, score.topic_fit))
        risks = next((candidate.get("risks", []) for candidate in candidates if candidate.get("id") == selected.candidate_id), [])
        return DraftCandidateSelection(
            selected_candidate_id=selected.candidate_id,
            reason="Selected by deterministic v1 score across constraints, evidence, topic, fabula, audience value, and risk.",
            scorecard=scores,
            unresolved_risks=[str(risk) for risk in risks[:3]],
        )

    def _score(self, candidate: dict[str, Any], *, provider_alternative_exists: bool) -> DraftCandidateScore:
        title = str(candidate.get("title") or "")
        body = str(candidate.get("body") or "")
        evidence = candidate.get("usedEvidence") if isinstance(candidate.get("usedEvidence"), list) else []
        coverage = candidate.get("ruleCoverage") if isinstance(candidate.get("ruleCoverage"), list) else []
        risks = candidate.get("risks") if isinstance(candidate.get("risks"), list) else []
        text = f"{title}\n{body}".lower()
        publishability = self._publishability_policy.evaluate(
            candidate,
            provider_alternative_exists=provider_alternative_exists,
        )
        return DraftCandidateScore(
            candidate_id=str(candidate.get("id") or ""),
            hard_constraint_fit=min(25, 10 + len(coverage) * 3),
            evidence_grounding=min(25, 8 + len(evidence) * 4),
            topic_fit=18 if "topic" in text or "ai" in text else 12,
            fabula_fit=18 if "conflict" in text or "thesis" in text or "конфликт" in text or "тезис" in text else 12,
            audience_value=14 if "practical" in text or "check" in text or "практи" in text else 10,
            risk_penalty=min(12, len(risks) * 2),
            publishable=publishability.publishable,
            selection_status=publishability.selection_status,
            selection_penalty=publishability.selection_penalty,
            selection_reasons=publishability.selection_reasons,
        )
