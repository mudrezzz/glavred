from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class SourceLedgerClaimType(StrEnum):
    BRIEF_INTENT = "briefIntent"
    CANDIDATE_CLAIM = "candidateClaim"
    SOURCE_CLAIM = "sourceClaim"
    TOPIC_FABULA_CONSTRAINT = "topicFabulaConstraint"
    AUTHOR_POSITION_EVIDENCE = "authorPositionEvidence"
    EXTERNAL_EVIDENCE = "externalEvidenceClaim"


class SourceLedgerAllowedUse(StrEnum):
    CAN_STATE = "canState"
    CAN_USE_AS_FRAMING = "canUseAsFraming"
    NEEDS_QUALIFICATION = "needsQualification"
    DO_NOT_STATE = "doNotState"


class SourceLedgerConfidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class SourceLedgerClaim:
    id: str
    claim_type: SourceLedgerClaimType
    statement: str
    source: str
    provenance: dict[str, Any]
    confidence: SourceLedgerConfidence
    allowed_use: SourceLedgerAllowedUse
    risk_flags: list[str] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.claim_type.value,
            "statement": self.statement,
            "source": self.source,
            "provenance": self.provenance,
            "confidence": self.confidence.value,
            "allowedUse": self.allowed_use.value,
            "riskFlags": self.risk_flags,
        }


@dataclass(frozen=True)
class SourceLedgerRisk:
    id: str
    title: str
    detail: str
    source: str
    severity: str = "medium"

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "detail": self.detail,
            "source": self.source,
            "severity": self.severity,
        }


@dataclass(frozen=True)
class ForbiddenInference:
    id: str
    statement: str
    reason: str
    source: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "statement": self.statement,
            "reason": self.reason,
            "source": self.source,
        }


@dataclass(frozen=True)
class SourceLedgerWarning:
    id: str
    title: str
    detail: str
    source: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "detail": self.detail,
            "source": self.source,
        }


@dataclass(frozen=True)
class SourceLedger:
    claims: list[SourceLedgerClaim] = field(default_factory=list)
    risks: list[SourceLedgerRisk] = field(default_factory=list)
    forbidden_inferences: list[ForbiddenInference] = field(default_factory=list)
    warnings: list[SourceLedgerWarning] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "claims": [claim.to_payload() for claim in self.claims],
            "risks": [risk.to_payload() for risk in self.risks],
            "forbiddenInferences": [item.to_payload() for item in self.forbidden_inferences],
            "warnings": [warning.to_payload() for warning in self.warnings],
            "metadata": {
                **self.metadata,
                "claimCount": len(self.claims),
                "riskCount": len(self.risks),
                "forbiddenInferenceCount": len(self.forbidden_inferences),
                "warningCount": len(self.warnings),
            },
        }
