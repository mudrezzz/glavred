import re
from typing import Any

from backend.app.application.draft_attribution_markers import DraftAttributionMarkerMatcher
from backend.app.application.draft_attribution_requirements import normalize_attribution_requirements
from backend.app.domain.draft_validation import DraftValidatorFinding, DraftValidatorStatus


NUMBER_PATTERN = re.compile(r"(\d+[%\w]*|[0-9]+[.,][0-9]+)")


def evidence_findings(
    *,
    candidate_id: str,
    body: str,
    candidate: dict[str, Any],
    context_artifact: dict[str, Any],
    material_plan: dict[str, Any],
    finding_factory: Any,
) -> list[DraftValidatorFinding]:
    findings: list[DraftValidatorFinding] = []
    material = _dict(material_plan.get("materialPlan"))
    rejected = _strings(material.get("rejectedEvidence") or material_plan.get("rejectedEvidence"))
    requirements = _list(material.get("claimsRequiringAttribution") or material_plan.get("claimsRequiringAttribution"))
    used_evidence = _strings(candidate.get("usedEvidence"))
    for evidence_id in rejected:
        if evidence_id in used_evidence or evidence_id.lower() in body.lower():
            findings.append(finding_factory(
                "evidence.rejected-proof",
                DraftValidatorStatus.CRITICAL,
                candidate_id,
                "Candidate uses rejected or planned evidence as proof.",
                evidence_id,
                "Remove the claim or replace it with accepted ledger evidence.",
                claim_ids=[evidence_id],
            ))
    external_claims = _external_claims(context_artifact)
    resolution = normalize_attribution_requirements(requirements, external_claims)
    requiring_attribution = _strings(resolution.get("resolvedClaimIds"))
    external_ids = [str(claim.get("id")) for claim in external_claims if claim.get("id")]
    attribution_claims = sorted(set(requiring_attribution + [claim_id for claim_id in external_ids if claim_id in used_evidence]))
    if attribution_claims and _looks_like_public_claim(body):
        attribution = DraftAttributionMarkerMatcher().evaluate(body=body, claims=external_claims, claim_ids=attribution_claims)
        attribution.update({
            "attributionRequirementResolution": resolution,
            "resolvedClaimIds": requiring_attribution,
            "unresolvedAttributionRequirements": resolution.get("unresolvedAttributionRequirements", []),
        })
        missing = _strings(attribution.get("missingClaimIds"))
        if missing:
            findings.append(finding_factory(
                "evidence.attribution",
                DraftValidatorStatus.WARNING,
                candidate_id,
                "Source-backed public claim needs visible attribution.",
                ", ".join(missing),
                "Name the source, source title, author, organization, or qualify the claim.",
                claim_ids=missing,
                metadata=attribution,
            ))
    unresolved = _list(resolution.get("unresolvedAttributionRequirements"))
    if unresolved:
        findings.append(finding_factory(
            "evidence.attribution.diagnostic",
            DraftValidatorStatus.NOT_RUN,
            candidate_id,
            "Some attribution requirements could not be resolved to source-backed claims.",
            "; ".join(str(_dict(item).get("requirement") or "") for item in unresolved)[:500],
            "Diagnostic only: normalize the material plan requirement to a claim id before treating it as actionable.",
            metadata={
                "unresolvedAttributionRequirements": unresolved,
                "resolvedClaimIds": requiring_attribution,
                "suppressedReason": "unresolved-attribution-requirement",
            },
        ))
    return findings


def _looks_like_public_claim(body: str) -> bool:
    markers = ("исслед", "report", "survey", "статист", "данн")
    return bool(NUMBER_PATTERN.search(body)) or any(marker in body.lower() for marker in markers)


def _external_claims(context_artifact: dict[str, Any]) -> list[dict[str, Any]]:
    claims = _list(_dict(context_artifact.get("sourceLedger")).get("claims"))
    return [claim for claim in (_dict(item) for item in claims) if claim.get("type") == "externalEvidenceClaim"]


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _strings(value: Any) -> list[str]:
    return [str(item).strip() for item in _list(value) if str(item).strip()]
