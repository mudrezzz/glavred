from typing import Any

from backend.app.application.draft_rule_pack_sections import as_list_of_dicts
from backend.app.domain.draft_rule_pack import RulePackRequirement, RulePackRule


def rules_from_registry(registry_snapshot: dict[str, Any], category: str) -> list[RulePackRule]:
    return [
        RulePackRule(
            id=str(rule.get("id")),
            category=category,
            title=str(rule.get("title") or category),
            statement=str(rule.get("statement") or ""),
            source=str(rule.get("source") or "ruleRegistry"),
            severity=str(rule.get("severity") or "normal"),
        )
        for rule in as_list_of_dicts(registry_snapshot.get("rules"))
        if rule.get("category") == category and rule.get("statement")
    ]


def requirements_from_registry(registry_snapshot: dict[str, Any], category: str) -> list[RulePackRequirement]:
    return [
        RulePackRequirement(
            id=str(rule.get("id")),
            category=category,
            title=str(rule.get("title") or category),
            detail=str(rule.get("statement") or ""),
            source=str(rule.get("source") or "ruleRegistry"),
        )
        for rule in as_list_of_dicts(registry_snapshot.get("rules"))
        if rule.get("category") == category and rule.get("statement")
    ]
