from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RhetoricalMove:
    label: str
    purpose: str
    claim_ids: list[str] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        return {"label": self.label, "purpose": self.purpose, "claimIds": self.claim_ids}


@dataclass(frozen=True)
class RhetoricalPlanClaimUse:
    claim_id: str
    use: str
    caution: str = ""

    def to_payload(self) -> dict[str, Any]:
        return {"claimId": self.claim_id, "use": self.use, "caution": self.caution}


@dataclass(frozen=True)
class RhetoricalPlan:
    id: str
    title: str
    angle: str
    opening_move: str
    moves: list[RhetoricalMove] = field(default_factory=list)
    claims_to_use: list[RhetoricalPlanClaimUse] = field(default_factory=list)
    claim_ids_to_avoid: list[str] = field(default_factory=list)
    required_rule_ids: list[str] = field(default_factory=list)
    size_intent: str = "standard"
    cta_route: str = ""
    risks: list[str] = field(default_factory=list)
    why_this_plan: str = ""

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "angle": self.angle,
            "openingMove": self.opening_move,
            "moves": [move.to_payload() for move in self.moves],
            "claimsToUse": [claim.to_payload() for claim in self.claims_to_use],
            "claimIdsToAvoid": self.claim_ids_to_avoid,
            "requiredRuleIds": self.required_rule_ids,
            "sizeIntent": self.size_intent,
            "ctaRoute": self.cta_route,
            "risks": self.risks,
            "whyThisPlan": self.why_this_plan,
        }


@dataclass(frozen=True)
class RhetoricalPlanSet:
    plans: list[RhetoricalPlan]

    def to_payload(self) -> dict[str, Any]:
        return {"plans": [plan.to_payload() for plan in self.plans]}


def rhetorical_plan_from_payload(payload: dict[str, Any], fallback_id: str) -> RhetoricalPlan:
    plan_id = str(payload.get("id") or fallback_id)
    return RhetoricalPlan(
        id=plan_id,
        title=str(payload.get("title") or plan_id),
        angle=str(payload.get("angle") or ""),
        opening_move=str(payload.get("openingMove") or ""),
        moves=[_move(item) for item in _records(payload.get("moves"))],
        claims_to_use=[_claim_use(item) for item in _records(payload.get("claimsToUse"))],
        claim_ids_to_avoid=_strings(payload.get("claimIdsToAvoid")),
        required_rule_ids=_strings(payload.get("requiredRuleIds")),
        size_intent=str(payload.get("sizeIntent") or "standard"),
        cta_route=str(payload.get("ctaRoute") or ""),
        risks=_strings(payload.get("risks")),
        why_this_plan=str(payload.get("whyThisPlan") or ""),
    )


def rhetorical_plan_set_from_payload(payload: dict[str, Any]) -> RhetoricalPlanSet:
    raw_plans = _records(payload.get("plans"))
    plans = [rhetorical_plan_from_payload(item, f"plan-{index + 1}") for index, item in enumerate(raw_plans)]
    return RhetoricalPlanSet(plans=plans)


def _move(payload: dict[str, Any]) -> RhetoricalMove:
    return RhetoricalMove(
        label=str(payload.get("label") or ""),
        purpose=str(payload.get("purpose") or ""),
        claim_ids=_strings(payload.get("claimIds")),
    )


def _claim_use(payload: dict[str, Any]) -> RhetoricalPlanClaimUse:
    return RhetoricalPlanClaimUse(
        claim_id=str(payload.get("claimId") or ""),
        use=str(payload.get("use") or ""),
        caution=str(payload.get("caution") or ""),
    )


def _records(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]
