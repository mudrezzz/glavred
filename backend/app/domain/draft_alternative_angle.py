from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AlternativeAngleRoute:
    id: str
    title: str
    angle: str
    opening_move: str
    why_different: str
    critique_inputs: list[str] = field(default_factory=list)
    claims_to_use: list[str] = field(default_factory=list)
    claims_to_avoid: list[str] = field(default_factory=list)
    rules_to_stress: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "angle": self.angle,
            "openingMove": self.opening_move,
            "whyDifferent": self.why_different,
            "critiqueInputs": self.critique_inputs,
            "claimsToUse": self.claims_to_use,
            "claimsToAvoid": self.claims_to_avoid,
            "rulesToStress": self.rules_to_stress,
            "risks": self.risks,
        }


@dataclass(frozen=True)
class AlternativeAngleTournament:
    status: str
    route: AlternativeAngleRoute | None = None
    candidate: dict[str, Any] | None = None
    attempts: list[dict[str, Any]] = field(default_factory=list)
    ai_run_ids: list[str] = field(default_factory=list)
    reason: str = ""

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": self.status,
            "attempts": self.attempts,
            "aiRunIds": self.ai_run_ids,
        }
        if self.route:
            payload["route"] = self.route.to_payload()
        if self.candidate:
            payload["candidate"] = self.candidate
        if self.reason:
            payload["reason"] = self.reason
        return payload


def alternative_route_from_payload(payload: dict[str, Any]) -> AlternativeAngleRoute:
    return AlternativeAngleRoute(
        id=str(payload.get("id") or "alternative-angle-1"),
        title=str(payload.get("title") or "Alternative angle"),
        angle=str(payload.get("angle") or ""),
        opening_move=str(payload.get("openingMove") or ""),
        why_different=str(payload.get("whyDifferent") or ""),
        critique_inputs=_strings(payload.get("critiqueInputs")),
        claims_to_use=_strings(payload.get("claimsToUse")),
        claims_to_avoid=_strings(payload.get("claimsToAvoid")),
        rules_to_stress=_strings(payload.get("rulesToStress")),
        risks=_strings(payload.get("risks")),
    )


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]
