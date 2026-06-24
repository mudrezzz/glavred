from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MaterialPlanAccountabilityResult:
    valid: bool
    invalid_reasons: list[str] = field(default_factory=list)
    accepted_evidence: list[str] = field(default_factory=list)
    rejected_evidence: list[str] = field(default_factory=list)
    rejection_reasons: list[str] = field(default_factory=list)
    claims_requiring_attribution: list[str] = field(default_factory=list)
    qualified_claims: list[str] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "invalidReasons": self.invalid_reasons,
            "acceptedEvidence": self.accepted_evidence,
            "rejectedEvidence": self.rejected_evidence,
            "rejectionReasons": self.rejection_reasons,
            "claimsRequiringAttribution": self.claims_requiring_attribution,
            "qualifiedClaims": self.qualified_claims,
        }


def evaluate_material_plan_accountability(
    *,
    material_plan_payload: dict[str, Any],
    usable_evidence_candidates: list[dict[str, Any]],
) -> MaterialPlanAccountabilityResult:
    accepted = _strings(material_plan_payload.get("availableEvidence"))
    rejected = _strings(material_plan_payload.get("rejectedEvidence"))
    rejection_reasons = _strings(material_plan_payload.get("rejectionReasons"))
    claims_requiring_attribution = _strings(material_plan_payload.get("claimsRequiringAttribution"))
    qualified_claims = _strings(material_plan_payload.get("qualifiedClaims"))
    invalid_reasons: list[str] = []

    if usable_evidence_candidates and not accepted:
        required_rejections = min(len(usable_evidence_candidates), 3)
        explained_rejections = len(rejected) + len(rejection_reasons)
        if explained_rejections < required_rejections:
            invalid_reasons.append(
                "materialPlan ignored usable evidence candidates without enough rejection reasons"
            )

    if accepted and usable_evidence_candidates:
        candidate_text = "\n".join(
            f"{item.get('claimId')} {item.get('statement')}" for item in usable_evidence_candidates
        ).lower()
        matched = [item for item in accepted if item.lower() in candidate_text or _mentions_claim_id(item, usable_evidence_candidates)]
        if not matched:
            invalid_reasons.append("availableEvidence does not reference projected source-ledger claims")

    return MaterialPlanAccountabilityResult(
        valid=len(invalid_reasons) == 0,
        invalid_reasons=invalid_reasons,
        accepted_evidence=accepted,
        rejected_evidence=rejected,
        rejection_reasons=rejection_reasons,
        claims_requiring_attribution=claims_requiring_attribution,
        qualified_claims=qualified_claims,
    )


def _mentions_claim_id(value: str, candidates: list[dict[str, Any]]) -> bool:
    normalized = value.lower()
    return any(str(item.get("claimId") or "").lower() in normalized for item in candidates)


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]
