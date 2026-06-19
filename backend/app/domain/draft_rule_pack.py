from dataclasses import dataclass, field
from typing import Any, Literal

RuleCategory = Literal[
    "hardConstraints",
    "softConstraints",
    "evidenceRequirements",
    "dramaturgyRequirements",
    "topicFitRequirements",
    "qualityRubric",
    "forbiddenMoves",
]


@dataclass(frozen=True)
class RulePackRule:
    id: str
    category: RuleCategory
    title: str
    statement: str
    source: str
    severity: str = "normal"

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "title": self.title,
            "statement": self.statement,
            "source": self.source,
            "severity": self.severity,
        }


@dataclass(frozen=True)
class RulePackRequirement:
    id: str
    category: RuleCategory
    title: str
    detail: str
    source: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "title": self.title,
            "detail": self.detail,
            "source": self.source,
        }


@dataclass(frozen=True)
class RulePack:
    draft_intent: dict[str, Any]
    hard_constraints: list[RulePackRule] = field(default_factory=list)
    soft_constraints: list[RulePackRule] = field(default_factory=list)
    evidence_requirements: list[RulePackRequirement] = field(default_factory=list)
    dramaturgy_requirements: list[RulePackRequirement] = field(default_factory=list)
    topic_fit_requirements: list[RulePackRequirement] = field(default_factory=list)
    quality_rubric: list[RulePackRequirement] = field(default_factory=list)
    forbidden_moves: list[RulePackRule] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    warnings: list[dict[str, Any]] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        return {
            "draftIntent": self.draft_intent,
            "hardConstraints": [item.to_payload() for item in self.hard_constraints],
            "softConstraints": [item.to_payload() for item in self.soft_constraints],
            "evidenceRequirements": [item.to_payload() for item in self.evidence_requirements],
            "dramaturgyRequirements": [item.to_payload() for item in self.dramaturgy_requirements],
            "topicFitRequirements": [item.to_payload() for item in self.topic_fit_requirements],
            "qualityRubric": [item.to_payload() for item in self.quality_rubric],
            "forbiddenMoves": [item.to_payload() for item in self.forbidden_moves],
            "metadata": self.metadata,
            "warnings": self.warnings,
        }
