from typing import Any

from backend.app.domain.draft_candidates import DraftCandidateDirection


class DraftCandidateDirectionService:
    def create_directions(
        self,
        *,
        context_summary: dict[str, Any],
        rule_pack: dict[str, Any],
        draft_strategy: dict[str, Any],
        rhetorical_plans: dict[str, Any] | None = None,
    ) -> list[DraftCandidateDirection]:
        plan_directions = _directions_from_plans(rhetorical_plans)
        if plan_directions:
            return plan_directions
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
def _directions_from_plans(payload: dict[str, Any] | None) -> list[DraftCandidateDirection]:
    plans = payload.get("plans") if isinstance(payload, dict) else None
    if not isinstance(plans, list):
        return []
    directions: list[DraftCandidateDirection] = []
    for index, item in enumerate(plans):
        plan = item if isinstance(item, dict) else {}
        plan_id = str(plan.get("id") or f"plan-{index + 1}")
        title = str(plan.get("title") or plan_id)
        angle = str(plan.get("angle") or plan.get("whyThisPlan") or title)
        instruction = str(plan.get("openingMove") or plan.get("ctaRoute") or angle)
        directions.append(
            DraftCandidateDirection(
                id=plan_id,
                title=title,
                angle=angle,
                instruction=instruction,
                rhetorical_plan_id=plan_id,
            )
        )
    return directions
def _get(payload: dict[str, Any], *path: str) -> Any:
    current: Any = payload
    for key in path:
        current = current.get(key) if isinstance(current, dict) else None
    return current
