from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class FeasibilityStatus(StrEnum):
    FEASIBLE = "feasible"
    FEASIBLE_WITH_CONSTRAINTS = "feasible_with_constraints"
    NEEDS_RESEARCH = "needs_research"
    NEEDS_HUMAN_DECISION = "needs_human_decision"
    INFEASIBLE = "infeasible"


@dataclass(frozen=True)
class FeasibilityFinding:
    id: str
    severity: str
    title: str
    detail: str
    source: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "severity": self.severity,
            "title": self.title,
            "detail": self.detail,
            "source": self.source,
        }


@dataclass(frozen=True)
class FeasibilityReport:
    status: FeasibilityStatus
    summary: str
    findings: list[FeasibilityFinding] = field(default_factory=list)
    allowed_claim_ids: list[str] = field(default_factory=list)
    qualified_claim_ids: list[str] = field(default_factory=list)
    blocked: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "summary": self.summary,
            "findings": [finding.to_payload() for finding in self.findings],
            "allowedClaimIds": self.allowed_claim_ids,
            "qualifiedClaimIds": self.qualified_claim_ids,
            "blocked": self.blocked,
            "metadata": self.metadata,
        }
