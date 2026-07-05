"""Owner: drafting.application.planning

Used by: DraftRun planning migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any


USABLE_ALLOWED_USE = {"canState", "needsQualification", "canUseAsFraming"}


class MaterialPlanEvidenceProjectionComponent:
    """Owns migrated helper behavior; module-level aliases remain compatibility-only."""

    @staticmethod
    def build_usable_evidence_candidates(
        *,
        context_artifact: dict[str, Any] | None,
        rule_pack: dict[str, Any],
        limit: int = 12,
    ) -> list[dict[str, Any]]:
        source_ledger = _as_dict((context_artifact or {}).get("sourceLedger"))
        post_contract = _as_dict((context_artifact or {}).get("postContract"))
        registry = _as_dict(rule_pack.get("ruleRegistrySnapshot"))
        contract_claim_ids = {
            str(item.get("id"))
            for item in _as_list_of_dicts(post_contract.get("claims"))
            if item.get("id")
        }
        registry_claim_ids = {
            str(claim_id)
            for rule in _as_list_of_dicts(registry.get("rules"))
            for claim_id in _as_list(rule.get("claimIds"))
            if str(claim_id).strip()
        }

        candidates = []
        for claim in _as_list_of_dicts(source_ledger.get("claims")):
            claim_id = str(claim.get("id") or "").strip()
            statement = str(claim.get("statement") or "").strip()
            allowed_use = str(claim.get("allowedUse") or "").strip()
            if not claim_id or not statement or allowed_use not in USABLE_ALLOWED_USE:
                continue
            provenance = _as_dict(claim.get("provenance"))
            candidates.append({
                "claimId": claim_id,
                "statement": statement,
                "allowedUse": allowed_use,
                "confidence": claim.get("confidence") or "unknown",
                "source": claim.get("source") or "sourceLedger",
                "sourceTitle": provenance.get("sourceTitle") or provenance.get("source") or "",
                "sourceUrl": provenance.get("sourceUrl") or "",
                "requiresAttribution": allowed_use in {"canState", "needsQualification"} or bool(provenance.get("sourceUrl")),
                "requiresQualification": allowed_use == "needsQualification",
                "priority": _priority(claim, claim_id, contract_claim_ids, registry_claim_ids),
            })

        return sorted(candidates, key=lambda item: (-int(item["priority"]), str(item["claimId"])))[:limit]

    @staticmethod
    def _priority(
        claim: dict[str, Any],
        claim_id: str,
        contract_claim_ids: set[str],
        registry_claim_ids: set[str],
    ) -> int:
        score = 0
        if claim_id in contract_claim_ids:
            score += 40
        if claim_id in registry_claim_ids:
            score += 20
        if claim.get("type") == "externalEvidenceClaim":
            score += 15
        if claim.get("allowedUse") == "canState":
            score += 10
        if claim.get("allowedUse") == "needsQualification":
            score += 6
        if claim.get("confidence") == "high":
            score += 8
        if claim.get("confidence") == "medium":
            score += 4
        return score

    @staticmethod
    def _as_dict(value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _as_list(value: Any) -> list[Any]:
        return value if isinstance(value, list) else []

    @staticmethod
    def _as_list_of_dicts(value: Any) -> list[dict[str, Any]]:
        return [item for item in _as_list(value) if isinstance(item, dict)]

build_usable_evidence_candidates = MaterialPlanEvidenceProjectionComponent.build_usable_evidence_candidates
_priority = MaterialPlanEvidenceProjectionComponent._priority
_as_dict = MaterialPlanEvidenceProjectionComponent._as_dict
_as_list = MaterialPlanEvidenceProjectionComponent._as_list
_as_list_of_dicts = MaterialPlanEvidenceProjectionComponent._as_list_of_dicts


__all__ = (
    'USABLE_ALLOWED_USE',
    'build_usable_evidence_candidates',
    'MaterialPlanEvidenceProjectionComponent',
)
