from typing import Any

from backend.app.domain.draft_evidence_synthesis import (
    EvidenceSynthesis,
    ExternalEvidenceClaim,
    ExternalEvidenceWarning,
)


class DeterministicExternalEvidenceSynthesisService:
    def synthesize(
        self,
        public_evidence: dict[str, Any],
        context_artifact: dict[str, Any] | None = None,
    ) -> EvidenceSynthesis:
        items = _items(public_evidence)
        attempts = _attempts(public_evidence)
        warnings = [
            ExternalEvidenceWarning(
                code="public-evidence-attempt-not-proof",
                message=f"{attempt.get('kind')}: {attempt.get('status')} is not merged as evidence.",
            )
            for attempt in attempts
            if attempt.get("status") not in {"succeeded"}
        ]
        if not items:
            warnings.append(ExternalEvidenceWarning(
                code="no-public-evidence-items",
                message="No accepted public evidence items were available for ledger merge.",
            ))
        return EvidenceSynthesis(
            source="deterministicFallback",
            external_claims=[_claim_from_item(item) for item in items],
            warnings=warnings,
            decisions=[{
                "decision": "conservative-merge",
                "detail": "Accepted public evidence was converted into qualified external claims without inventing new facts.",
            }],
            metadata={"version": "evidence-synthesis-v1", "itemCount": len(items)},
        )


def _claim_from_item(item: dict[str, Any]) -> ExternalEvidenceClaim:
    summary = str(item.get("textSummary") or item.get("snippet") or "").strip()
    title = str(item.get("sourceTitle") or "Public source").strip()
    statement = summary[:420].rstrip() or title
    return ExternalEvidenceClaim(
        public_evidence_item_id=str(item.get("id") or ""),
        statement=statement,
        allowed_use=str(item.get("allowedUse") or "needsQualification"),
        confidence=str(item.get("confidence") or "medium"),
        decision="mergeQualifiedClaim",
        rationale=f"Accepted public evidence from {title}; use as qualified support until validators check exact grounding.",
        risk_flags=["external-evidence-needs-validation"],
    )


def _items(public_evidence: dict[str, Any]) -> list[dict[str, Any]]:
    items = public_evidence.get("items")
    return [item for item in items if isinstance(item, dict)] if isinstance(items, list) else []


def _attempts(public_evidence: dict[str, Any]) -> list[dict[str, Any]]:
    attempts = public_evidence.get("attempts")
    return [item for item in attempts if isinstance(item, dict)] if isinstance(attempts, list) else []
