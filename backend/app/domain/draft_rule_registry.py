from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class RuleRegistrySeverity(StrEnum):
    HARD = "hard"
    SOFT = "soft"
    WARNING = "warning"


class RuleRegistryValidatorType(StrEnum):
    DETERMINISTIC = "deterministic"
    LLM = "llm"
    HUMAN_REVIEW = "humanReview"
    NONE = "none"


@dataclass(frozen=True)
class RuleBinding:
    validator_type: RuleRegistryValidatorType
    observable_criteria: list[str] = field(default_factory=list)
    repair_policy: str = "report"

    def to_payload(self) -> dict[str, Any]:
        return {
            "validatorType": self.validator_type.value,
            "observableCriteria": self.observable_criteria,
            "repairPolicy": self.repair_policy,
        }


@dataclass(frozen=True)
class RuleRegistryRule:
    id: str
    source: str
    scope: str
    category: str
    title: str
    statement: str
    priority: int
    severity: RuleRegistrySeverity
    binding: RuleBinding
    condition: str | None = None
    claim_ids: list[str] = field(default_factory=list)
    contract_refs: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "scope": self.scope,
            "category": self.category,
            "title": self.title,
            "statement": self.statement,
            "priority": self.priority,
            "severity": self.severity.value,
            "condition": self.condition,
            "binding": self.binding.to_payload(),
            "claimIds": self.claim_ids,
            "contractRefs": self.contract_refs,
            "examples": self.examples,
        }


@dataclass(frozen=True)
class RuleRegistrySnapshot:
    rules: list[RuleRegistryRule]
    metadata: dict[str, Any] = field(default_factory=dict)
    warnings: list[dict[str, Any]] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        return {
            "version": "rule-registry-v2",
            "rules": [rule.to_payload() for rule in sorted(self.rules, key=lambda item: (item.priority, item.id))],
            "metadata": {**self.metadata, "ruleCount": len(self.rules), **_counts(self.rules)},
            "warnings": self.warnings,
        }


def _counts(rules: list[RuleRegistryRule]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {"bySeverity": {}, "byCategory": {}, "byValidatorType": {}}
    for rule in rules:
        result["bySeverity"][rule.severity.value] = result["bySeverity"].get(rule.severity.value, 0) + 1
        result["byCategory"][rule.category] = result["byCategory"].get(rule.category, 0) + 1
        validator_type = rule.binding.validator_type.value
        result["byValidatorType"][validator_type] = result["byValidatorType"].get(validator_type, 0) + 1
    return result
