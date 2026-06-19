from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MaterialPlan:
    available_evidence: list[str] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    risky_claims: list[str] = field(default_factory=list)
    grounding_plan: list[str] = field(default_factory=list)
    source_notes: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        return {
            "availableEvidence": self.available_evidence,
            "missingEvidence": self.missing_evidence,
            "riskyClaims": self.risky_claims,
            "groundingPlan": self.grounding_plan,
            "sourceNotes": self.source_notes,
            "openQuestions": self.open_questions,
        }


@dataclass(frozen=True)
class DraftStrategy:
    thesis_angle: str
    opening_move: str
    argument_sequence: list[str] = field(default_factory=list)
    fabula_usage: str = ""
    cta_plan: str = ""
    forbidden_moves: list[str] = field(default_factory=list)
    tone_notes: list[str] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        return {
            "thesisAngle": self.thesis_angle,
            "openingMove": self.opening_move,
            "argumentSequence": self.argument_sequence,
            "fabulaUsage": self.fabula_usage,
            "ctaPlan": self.cta_plan,
            "forbiddenMoves": self.forbidden_moves,
            "toneNotes": self.tone_notes,
        }


def material_plan_from_payload(payload: dict[str, Any]) -> MaterialPlan:
    return MaterialPlan(
        available_evidence=_strings(payload.get("availableEvidence")),
        missing_evidence=_strings(payload.get("missingEvidence")),
        risky_claims=_strings(payload.get("riskyClaims")),
        grounding_plan=_strings(payload.get("groundingPlan")),
        source_notes=_strings(payload.get("sourceNotes")),
        open_questions=_strings(payload.get("openQuestions")),
    )


def draft_strategy_from_payload(payload: dict[str, Any]) -> DraftStrategy:
    return DraftStrategy(
        thesis_angle=str(payload.get("thesisAngle") or ""),
        opening_move=str(payload.get("openingMove") or ""),
        argument_sequence=_strings(payload.get("argumentSequence")),
        fabula_usage=str(payload.get("fabulaUsage") or ""),
        cta_plan=str(payload.get("ctaPlan") or ""),
        forbidden_moves=_strings(payload.get("forbiddenMoves")),
        tone_notes=_strings(payload.get("toneNotes")),
    )


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]
