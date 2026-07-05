"""Owner: drafting.application.final_quality

Used by: DraftRun final_quality package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.validation.draft_attribution_requirements import normalize_attribution_requirements


def build_final_quality_contract(
    *,
    context_artifact: dict[str, Any],
    rule_pack: dict[str, Any],
    material_plan: dict[str, Any],
) -> dict[str, Any]:
    post_contract = _dict(context_artifact.get("postContract")) or _dict(context_artifact.get("post_contract"))
    if not post_contract:
        post_contract = _dict(context_artifact.get("postContractArtifact"))
    fabula = _dict(context_artifact.get("fabula")) or _dict(_dict(context_artifact.get("draftContext")).get("fabula"))
    size_contract = _dict(post_contract.get("publicationSizeContract"))
    publication_kind = str(size_contract.get("publicationKind") or _dict(context_artifact.get("publicationSizeProfile")).get("publicationKind") or "post")
    research_depth = str(fabula.get("researchDepth") or "standard")
    source_policy = _source_policy(research_depth, publication_kind)
    attribution = _attribution_requirements(context_artifact, material_plan)
    return {
        "version": "final-quality-contract-v1",
        "researchDepth": research_depth,
        "publicationKind": publication_kind,
        "fabulaSizeIntent": str(fabula.get("sizeIntent") or "standard"),
        "thesis": str(post_contract.get("thesis") or _dict(context_artifact.get("brief")).get("thesis") or ""),
        "audience": str(post_contract.get("audience") or ""),
        "cta": str(post_contract.get("cta") or ""),
        "sourceIntegrationPolicy": source_policy,
        "authorVoicePolicy": _author_voice_policy(fabula, post_contract),
        "examplePolicy": _example_policy(research_depth),
        "forbiddenPublicTerms": ["SourceLedger", "publicEvidence", "validators", "PostContract", "RuleRegistry"],
        "sourceAttributionRequired": attribution["resolvedClaimIds"],
        "unresolvedAttributionRequirements": attribution["unresolvedAttributionRequirements"],
        "attributionRequirementMatches": attribution["requirementMatches"],
        "qualifiedClaimIds": _claim_ids(material_plan, "qualifiedClaims"),
        "hardRuleIds": _hard_rule_ids(rule_pack),
        "acceptanceCriteria": [
            "The final text must satisfy the locked thesis, audience, value, and CTA.",
            "Source references must support author interpretation, not replace it.",
            "Concrete examples must be source-backed or explicitly marked as hypothetical.",
            "Internal pipeline terms must not appear as public prose.",
            "The allowed source density depends on researchDepth and publicationKind.",
        ],
    }


def _source_policy(research_depth: str, publication_kind: str) -> dict[str, Any]:
    style = {
        "light": "lightSupport",
        "standard": "balanced",
        "deep": "researchHeavy",
        "marketResearch": "researchHeavy",
    }.get(research_depth, "balanced")
    if "article" in publication_kind.lower() and style == "balanced":
        style = "researchHeavy"
    return {
        "style": style,
        "maxSourceSentenceShare": {"light": 0.2, "standard": 0.35, "deep": 0.5, "marketResearch": 0.65}.get(research_depth, 0.35),
        "requiresInterpretationAfterSources": True,
        "allowsSourceHeavyProse": style == "researchHeavy",
    }


def _author_voice_policy(fabula: dict[str, Any], post_contract: dict[str, Any]) -> dict[str, str]:
    return {
        "mode": str(fabula.get("authorVoice") or post_contract.get("authorVoice") or "contract-derived"),
        "source": "fabula-or-contract" if fabula.get("authorVoice") or post_contract.get("authorVoice") else "implicit",
    }


def _example_policy(research_depth: str) -> dict[str, str]:
    return {
        "mode": "hypotheticalAllowedWithMarker",
        "source": "default",
        "note": "Unbacked concrete examples must be explicitly framed as hypothetical scenarios.",
        "strictness": "high" if research_depth in {"deep", "marketResearch"} else "medium",
    }


def _claim_ids(payload: dict[str, Any], key: str) -> list[str]:
    material = _dict(payload.get("materialPlan"))
    values = material.get(key) or payload.get(key)
    ids: list[str] = []
    for item in _list(values):
        row = _dict(item)
        if row.get("claimId"):
            ids.append(str(row["claimId"]))
        elif isinstance(item, str) and "claimId" in item:
            ids.append(item[:180])
    return ids[:20]


def _attribution_requirements(context_artifact: dict[str, Any], material_plan: dict[str, Any]) -> dict[str, Any]:
    material = _dict(material_plan.get("materialPlan"))
    values = material.get("claimsRequiringAttribution") or material_plan.get("claimsRequiringAttribution") or []
    return normalize_attribution_requirements(_list(values), _external_claims(context_artifact))


def _external_claims(context_artifact: dict[str, Any]) -> list[dict[str, Any]]:
    ledger = _dict(context_artifact.get("sourceLedger"))
    claims = _list(ledger.get("claims"))
    return [claim for claim in (_dict(item) for item in claims) if claim.get("type") == "externalEvidenceClaim"]


def _hard_rule_ids(rule_pack: dict[str, Any]) -> list[str]:
    snapshot = _dict(rule_pack.get("ruleRegistrySnapshot"))
    ids: list[str] = []
    for rule in _list(snapshot.get("rules")):
        row = _dict(rule)
        if str(row.get("severity") or "").lower() == "hard" or str(row.get("category") or "").lower().startswith("hard"):
            ids.append(str(row.get("id") or ""))
    return [item for item in ids if item][:30]


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
