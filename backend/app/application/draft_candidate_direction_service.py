from typing import Any

from backend.app.domain.draft_candidates import DraftCandidateDirection


class DraftCandidateDirectionService:
    def create_directions(
        self,
        *,
        context_summary: dict[str, Any],
        rule_pack: dict[str, Any],
        draft_strategy: dict[str, Any],
    ) -> list[DraftCandidateDirection]:
        topic = _get(context_summary, "topic", "title") or _get(context_summary, "brief", "rubric") or "topic"
        thesis = draft_strategy.get("thesisAngle") or _get(rule_pack, "draftIntent", "thesis") or "main thesis"
        fabula = _get(context_summary, "fabula", "title") or draft_strategy.get("fabulaUsage") or "fabula"
        return [
            DraftCandidateDirection(
                id="research",
                title="Analytical research draft",
                angle=f"Explain {topic} through evidence and the thesis: {thesis}.",
                instruction="Use a calm analytical structure with explicit evidence and practical implications.",
            ),
            DraftCandidateDirection(
                id="polemic",
                title="Contrast-driven draft",
                angle=f"Frame the conflict sharply through {fabula} and show what common belief fails.",
                instruction="Open with a tension, contrast false comfort with the author position, and resolve through the CTA.",
            ),
            DraftCandidateDirection(
                id="checklist",
                title="Practical checklist draft",
                angle=f"Turn {topic} into concrete checks while preserving the approved fabula.",
                instruction="Make the draft operational: steps, checks, examples, and a practical closing.",
            ),
        ]


def _get(payload: dict[str, Any], *path: str) -> Any:
    current: Any = payload
    for key in path:
        current = current.get(key) if isinstance(current, dict) else None
    return current
