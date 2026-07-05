"""Owner: drafting.application.generation

Used by: DraftRun generation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from backend.app.domain.draft_candidates import DraftCandidate, DraftCandidateDirection
from backend.app.domain.draft_generation import DraftGenerationRequest


class DeterministicDraftCandidateService:
    def create_candidate(
        self,
        *,
        request: DraftGenerationRequest,
        direction: DraftCandidateDirection,
        rule_pack: dict,
        material_plan: dict,
    ) -> DraftCandidate:
        brief = request.brief
        evidence = material_plan.get("availableEvidence") or brief.evidence
        rule_titles = _rule_titles(rule_pack)
        body = "\n\n".join(
            [
                brief.title,
                direction.angle,
                f"Тезис: {brief.thesis}",
                f"Конфликт: {brief.conflict}",
                f"Позиция автора: {brief.author_position}",
                "Доказательства: " + "; ".join(evidence[:4]),
                "Практический вывод: " + (brief.cta or "проверить решение на реальном workflow."),
            ]
        )
        return DraftCandidate(
            id=f"candidate-{direction.id}-{brief.id}",
            direction=direction,
            title=f"{brief.title}: {direction.id}",
            body=body,
            rationale=f"Deterministic fallback follows the {direction.id} direction and approved brief.",
            used_evidence=list(evidence[:4]),
            rule_coverage=rule_titles[:6],
            risks=brief.risks[:3],
            weaknesses=["Needs provider rewrite before publication"],
        )


def _rule_titles(rule_pack: dict) -> list[str]:
    titles: list[str] = []
    for section in (
        "hardConstraints",
        "softConstraints",
        "topicFitRequirements",
        "dramaturgyRequirements",
        "evidenceRequirements",
    ):
        for item in rule_pack.get(section, []):
            if isinstance(item, dict):
                title = str(item.get("title") or item.get("text") or "").strip()
                if title:
                    titles.append(title)
    return titles
