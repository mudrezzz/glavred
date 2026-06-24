from typing import Any


class SourceLedgerExternalEvidenceMerger:
    def merge(
        self,
        *,
        source_ledger: dict[str, Any],
        public_evidence: dict[str, Any],
        evidence_synthesis: dict[str, Any],
    ) -> dict[str, Any]:
        merged = {
            **source_ledger,
            "claims": [*_claims(source_ledger), *self._external_claims(public_evidence, evidence_synthesis)],
            "warnings": [*_warnings(source_ledger), *self._external_warnings(public_evidence, evidence_synthesis)],
        }
        metadata = _as_dict(source_ledger.get("metadata"))
        external_count = len([claim for claim in merged["claims"] if claim.get("type") == "externalEvidenceClaim"])
        merged["metadata"] = {
            **metadata,
            "version": "source-ledger-v2-external-evidence",
            "externalClaimCount": external_count,
            "internalClaimCount": max(0, len(merged["claims"]) - external_count),
            "evidenceSynthesisSource": evidence_synthesis.get("source"),
            "claimCount": len(merged["claims"]),
            "warningCount": len(merged["warnings"]),
        }
        return merged

    def _external_claims(self, public_evidence: dict[str, Any], evidence_synthesis: dict[str, Any]) -> list[dict[str, Any]]:
        items_by_id = {str(item.get("id")): item for item in _items(public_evidence) if item.get("id")}
        result = []
        for claim in _synthesis_claims(evidence_synthesis):
            item_id = str(claim.get("publicEvidenceItemId") or "")
            item = items_by_id.get(item_id)
            if not item:
                continue
            result.append({
                "id": f"external-evidence-{item_id}",
                "type": "externalEvidenceClaim",
                "statement": str(claim.get("statement") or item.get("textSummary") or item.get("snippet") or ""),
                "source": "publicEvidence",
                "provenance": {
                    "publicEvidenceItemId": item_id,
                    "attemptId": item.get("attemptId"),
                    "sourceUrl": item.get("sourceUrl"),
                    "sourceTitle": item.get("sourceTitle"),
                    "snippet": item.get("snippet"),
                    "rationale": claim.get("rationale"),
                },
                "confidence": _confidence(str(claim.get("confidence") or item.get("confidence") or "medium")),
                "allowedUse": _allowed_use(str(claim.get("allowedUse") or item.get("allowedUse") or "needsQualification")),
                "riskFlags": [*([str(flag) for flag in claim.get("riskFlags") or [] if flag]), "external-evidence"],
            })
        return result

    def _external_warnings(self, public_evidence: dict[str, Any], evidence_synthesis: dict[str, Any]) -> list[dict[str, Any]]:
        warnings = []
        for warning in _as_list(public_evidence.get("warnings")):
            if isinstance(warning, dict):
                warnings.append({
                    "id": f"public-evidence-{warning.get('code') or len(warnings) + 1}",
                    "title": str(warning.get("code") or "Public evidence warning"),
                    "detail": str(warning.get("message") or ""),
                    "source": "publicEvidence",
                })
        for warning in _as_list(evidence_synthesis.get("warnings")):
            if isinstance(warning, dict):
                warnings.append({
                    "id": f"evidence-synthesis-{warning.get('code') or len(warnings) + 1}",
                    "title": str(warning.get("code") or "Evidence synthesis warning"),
                    "detail": str(warning.get("message") or ""),
                    "source": "evidenceSynthesis",
                })
        if not self._external_claims(public_evidence, evidence_synthesis):
            warnings.append({
                "id": "external-evidence-none-merged",
                "title": "No external evidence claims merged",
                "detail": "Public evidence did not produce accepted ledger claims for this run.",
                "source": "evidenceSynthesis",
            })
        return warnings


def _claims(source_ledger: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in _as_list(source_ledger.get("claims")) if isinstance(item, dict)]


def _warnings(source_ledger: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in _as_list(source_ledger.get("warnings")) if isinstance(item, dict)]


def _items(public_evidence: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in _as_list(public_evidence.get("items")) if isinstance(item, dict)]


def _synthesis_claims(evidence_synthesis: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in _as_list(evidence_synthesis.get("externalClaims")) if isinstance(item, dict)]


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _allowed_use(value: str) -> str:
    return value if value in {"canState", "needsQualification", "canUseAsFraming", "doNotState"} else "needsQualification"


def _confidence(value: str) -> str:
    return value if value in {"high", "medium", "low", "unknown"} else "medium"
