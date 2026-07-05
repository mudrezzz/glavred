"""Owner: drafting.application.evidence

Used by: DraftRun evidence migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.evidence.draft_rule_pack_sections import as_list_of_dicts
from backend.app.domain.draft_rule_pack import RulePackRequirement, RulePackRule


class RulePackFromRegistryComponent:
    """Owns migrated helper behavior; module-level aliases remain compatibility-only."""

    @staticmethod
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

    @staticmethod
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

rules_from_registry = RulePackFromRegistryComponent.rules_from_registry
requirements_from_registry = RulePackFromRegistryComponent.requirements_from_registry


__all__ = (
    'rules_from_registry',
    'requirements_from_registry',
    'RulePackFromRegistryComponent',
)
