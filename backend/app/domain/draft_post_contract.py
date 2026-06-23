from dataclasses import dataclass, field
from typing import Any

from backend.app.domain.publication_size import PublicationSizeContract


@dataclass(frozen=True)
class PostContractClaim:
    id: str
    allowed_use: str
    qualification: str | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "allowedUse": self.allowed_use,
            "qualification": self.qualification,
        }


@dataclass(frozen=True)
class PostContractObligation:
    id: str
    kind: str
    statement: str
    source: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "statement": self.statement,
            "source": self.source,
        }


@dataclass(frozen=True)
class PostContract:
    title: str
    thesis: str
    audience: str | None
    value: str | None
    goal: str | None
    cta: str | None
    platform: str | None
    date: str | None
    time: str | None
    topic_id: str | None
    topic_title: str | None
    fabula_id: str | None
    fabula_title: str | None
    claims: list[PostContractClaim] = field(default_factory=list)
    forbidden_moves: list[str] = field(default_factory=list)
    evidence_obligations: list[PostContractObligation] = field(default_factory=list)
    fabula_obligations: list[PostContractObligation] = field(default_factory=list)
    publication_size_contract: PublicationSizeContract | None = None
    risk_notes: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "status": "created",
            "title": self.title,
            "thesis": self.thesis,
            "audience": self.audience,
            "value": self.value,
            "goal": self.goal,
            "cta": self.cta,
            "platform": self.platform,
            "date": self.date,
            "time": self.time,
            "topic": {"id": self.topic_id, "title": self.topic_title},
            "fabula": {"id": self.fabula_id, "title": self.fabula_title},
            "claims": [claim.to_payload() for claim in self.claims],
            "forbiddenMoves": self.forbidden_moves,
            "evidenceObligations": [item.to_payload() for item in self.evidence_obligations],
            "fabulaObligations": [item.to_payload() for item in self.fabula_obligations],
            "publicationSizeContract": self.publication_size_contract.to_payload() if self.publication_size_contract else None,
            "riskNotes": self.risk_notes,
            "metadata": self.metadata,
        }
