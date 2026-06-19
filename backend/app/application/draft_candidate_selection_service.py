from backend.app.domain.draft_candidates import DraftCandidateSelection, DraftCandidateScore


class DraftCandidateSelectionService:
    def select(self, candidates: list[dict]) -> DraftCandidateSelection:
        scores = [self._score(candidate) for candidate in candidates]
        selected = max(scores, key=lambda score: (score.total, score.evidence_grounding, score.topic_fit))
        risks = next((candidate.get("risks", []) for candidate in candidates if candidate.get("id") == selected.candidate_id), [])
        return DraftCandidateSelection(
            selected_candidate_id=selected.candidate_id,
            reason="Selected by deterministic v1 score across constraints, evidence, topic, fabula, audience value, and risk.",
            scorecard=scores,
            unresolved_risks=[str(risk) for risk in risks[:3]],
        )

    def _score(self, candidate: dict) -> DraftCandidateScore:
        title = str(candidate.get("title") or "")
        body = str(candidate.get("body") or "")
        evidence = candidate.get("usedEvidence") if isinstance(candidate.get("usedEvidence"), list) else []
        coverage = candidate.get("ruleCoverage") if isinstance(candidate.get("ruleCoverage"), list) else []
        risks = candidate.get("risks") if isinstance(candidate.get("risks"), list) else []
        text = f"{title}\n{body}".lower()
        return DraftCandidateScore(
            candidate_id=str(candidate.get("id") or ""),
            hard_constraint_fit=min(25, 10 + len(coverage) * 3),
            evidence_grounding=min(25, 8 + len(evidence) * 4),
            topic_fit=18 if "topic" in text or "ai" in text else 12,
            fabula_fit=18 if "конфликт" in text or "тезис" in text else 12,
            audience_value=14 if "практи" in text or "check" in text else 10,
            risk_penalty=min(12, len(risks) * 2),
        )
