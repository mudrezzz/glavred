from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExternalEvidenceClaim:
    public_evidence_item_id: str
    statement: str
    allowed_use: str
    confidence: str
    decision: str
    rationale: str
    risk_flags: list[str] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        return {
            "publicEvidenceItemId": self.public_evidence_item_id,
            "statement": self.statement,
            "allowedUse": self.allowed_use,
            "confidence": self.confidence,
            "decision": self.decision,
            "rationale": self.rationale,
            "riskFlags": self.risk_flags,
        }


@dataclass(frozen=True)
class ExternalEvidenceWarning:
    code: str
    message: str
    public_evidence_item_id: str | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "publicEvidenceItemId": self.public_evidence_item_id,
        }


@dataclass(frozen=True)
class EvidenceSynthesis:
    source: str
    external_claims: list[ExternalEvidenceClaim] = field(default_factory=list)
    warnings: list[ExternalEvidenceWarning] = field(default_factory=list)
    decisions: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "externalClaims": [claim.to_payload() for claim in self.external_claims],
            "warnings": [warning.to_payload() for warning in self.warnings],
            "decisions": self.decisions,
            "metadata": {
                **self.metadata,
                "externalClaimCount": len(self.external_claims),
                "warningCount": len(self.warnings),
            },
        }
