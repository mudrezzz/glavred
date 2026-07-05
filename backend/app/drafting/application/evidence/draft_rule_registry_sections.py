"""Owner: drafting.application.evidence

Used by: DraftRun evidence migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.domain.draft_rule_registry import (
    RuleBinding,
    RuleRegistryRule,
    RuleRegistrySeverity,
    RuleRegistryValidatorType,
)

HARD_PUBLISHER_GROUPS = {"antiAiPattern", "forbiddenTopic", "forbiddenTopics", "positioning"}


class RuleRegistrySectionsComponent:
    """Owns migrated helper behavior; module-level aliases remain compatibility-only."""

    @staticmethod
    def publisher_rule_registry(publisher_rules: dict[str, Any]) -> list[RuleRegistryRule]:
        rules: list[RuleRegistryRule] = []
        for group, items in as_dict(publisher_rules.get("groups")).items():
            for index, item in enumerate(iter_rule_items(items)):
                statement = item.get("statement") or item.get("value")
                if not statement:
                    continue
                severity = RuleRegistrySeverity.HARD if group in HARD_PUBLISHER_GROUPS else RuleRegistrySeverity.SOFT
                category = "hardConstraints" if severity == RuleRegistrySeverity.HARD else "softConstraints"
                rules.append(
                    registry_rule(
                        f"publisher:{group}:{item.get('id') or index}",
                        category,
                        item.get("title") or group,
                        statement,
                        f"publisherRules.{group}",
                        severity,
                        validator=RuleRegistryValidatorType.LLM,
                        criteria=[f"Draft follows publisher rule group {group}."],
                        priority=20 if severity == RuleRegistrySeverity.HARD else 60,
                        scope="publisher",
                    )
                )
        return rules

    @staticmethod
    def topic_fabula_registry(topic: dict[str, Any], fabula: dict[str, Any]) -> list[RuleRegistryRule]:
        rules: list[RuleRegistryRule] = []
        for item_id, title, statement in (
            ("topic:purpose", "Topic purpose", topic.get("purpose")),
            ("topic:audienceValue", "Audience value", topic.get("audienceValue")),
            ("topic:authorStance", "Author stance", topic.get("authorStance")),
        ):
            if statement:
                rules.append(registry_rule(item_id, "topicFitRequirements", title, statement, "topic", RuleRegistrySeverity.SOFT))
        rules.extend(
            registry_rule(
                f"topic:rule:{index}", "topicFitRequirements", "Topic rule", item, "topic.rules", RuleRegistrySeverity.SOFT
            )
            for index, item in enumerate(as_list(topic.get("rules")))
        )
        rules.extend(
            registry_rule(
                f"topic:forbidden:{index}",
                "forbiddenMoves",
                "Forbidden topic angle",
                item,
                "topic.forbiddenAngles",
                RuleRegistrySeverity.HARD,
                validator=RuleRegistryValidatorType.DETERMINISTIC,
                priority=10,
            )
            for index, item in enumerate(as_list(topic.get("forbiddenAngles")))
        )
        if fabula.get("dramaturgy"):
            rules.append(
                registry_rule(
                    "fabula:dramaturgy",
                    "dramaturgyRequirements",
                    "Fabula dramaturgy",
                    fabula["dramaturgy"],
                    "fabula",
                    RuleRegistrySeverity.HARD,
                    priority=30,
                )
            )
        rules.extend(
            registry_rule(
                f"fabula:proof:{index}",
                "evidenceRequirements",
                "Fabula proof",
                item,
                "fabula",
                RuleRegistrySeverity.HARD,
                priority=30,
            )
            for index, item in enumerate(as_list(fabula.get("proofRequirements")))
        )
        return [rule for rule in rules if rule.statement]

    @staticmethod
    def direct_context_registry(candidate: dict[str, Any], signal: dict[str, Any]) -> list[RuleRegistryRule]:
        rules: list[RuleRegistryRule] = []
        for key, title in (("thesis", "Candidate thesis"), ("value", "Candidate value"), ("goal", "Candidate goal")):
            if candidate.get(key):
                rules.append(
                    registry_rule(
                        f"candidate:{key}",
                        "hardConstraints",
                        title,
                        candidate[key],
                        "candidate",
                        RuleRegistrySeverity.HARD,
                        priority=18,
                        scope="candidate",
                    )
                )
        if candidate.get("evidenceSummary"):
            rules.append(
                registry_rule(
                    "candidate:evidenceSummary",
                    "evidenceRequirements",
                    "Candidate evidence",
                    candidate["evidenceSummary"],
                    "candidate",
                    RuleRegistrySeverity.HARD,
                    priority=30,
                    scope="candidate",
                )
            )
        rules.extend(
            registry_rule(
                f"candidate:risk:{index}",
                "forbiddenMoves",
                "Candidate risk",
                item,
                "candidate",
                RuleRegistrySeverity.WARNING,
                validator=RuleRegistryValidatorType.HUMAN_REVIEW,
                priority=45,
                scope="candidate",
            )
            for index, item in enumerate(as_list(candidate.get("risks")))
        )
        for item_id, title, statement in (
            ("signal:summary", "Signal grounding", signal.get("summary")),
            ("signal:rawNote", "Signal raw note", signal.get("rawNote")),
        ):
            if statement:
                rules.append(
                    registry_rule(
                        item_id,
                        "evidenceRequirements",
                        title,
                        statement,
                        "sourceSignal",
                        RuleRegistrySeverity.HARD,
                        priority=30,
                        scope="sourceSignal",
                    )
                )
        return [rule for rule in rules if rule.statement]

    @staticmethod
    def ledger_registry(ledger: dict[str, Any]) -> list[RuleRegistryRule]:
        rules: list[RuleRegistryRule] = []
        for claim in as_list_of_dicts(ledger.get("claims")):
            claim_id = str(claim.get("id") or "")
            if not claim_id:
                continue
            allowed_use = str(claim.get("allowedUse") or "")
            severity = RuleRegistrySeverity.WARNING if allowed_use == "needsQualification" else RuleRegistrySeverity.SOFT
            validator = RuleRegistryValidatorType.HUMAN_REVIEW if allowed_use == "doNotState" else RuleRegistryValidatorType.LLM
            rules.append(
                registry_rule(
                    f"ledger:claim:{claim_id}",
                    "evidenceRequirements",
                    "Source claim use",
                    claim.get("statement"),
                    str(claim.get("source") or "sourceLedger"),
                    severity,
                    validator=validator,
                    criteria=[f"Claim {claim_id} is used only as {allowed_use or 'declared'}."],
                    priority=35,
                    claim_ids=[claim_id],
                    scope="sourceLedger",
                )
            )
        for item in as_list_of_dicts(ledger.get("forbiddenInferences")):
            item_id = str(item.get("id") or len(rules))
            rules.append(
                registry_rule(
                    f"ledger:forbidden:{item_id}",
                    "forbiddenMoves",
                    "Forbidden inference",
                    item.get("statement"),
                    str(item.get("source") or "sourceLedger"),
                    RuleRegistrySeverity.HARD,
                    validator=RuleRegistryValidatorType.DETERMINISTIC,
                    criteria=[str(item.get("reason") or "Do not make this inference.")],
                    priority=5,
                    scope="sourceLedger",
                )
            )
        return [rule for rule in rules if rule.statement]

    @staticmethod
    def brief_intent_registry(brief: dict[str, Any]) -> list[RuleRegistryRule]:
        fields = [
            ("brief:title", "hardConstraints", "Approved title", brief.get("title")),
            ("brief:thesis", "hardConstraints", "Approved thesis", brief.get("thesis")),
            ("brief:conflict", "dramaturgyRequirements", "Approved conflict", brief.get("conflict")),
            ("brief:authorPosition", "softConstraints", "Approved author position", brief.get("authorPosition")),
        ]
        return [
            registry_rule(item_id, category, title, statement, "brief", RuleRegistrySeverity.HARD if category != "softConstraints" else RuleRegistrySeverity.SOFT)
            for item_id, category, title, statement in fields
            if statement
        ]

    @staticmethod
    def registry_rule(
        item_id: str,
        category: str,
        title: Any,
        statement: Any,
        source: str,
        severity: RuleRegistrySeverity,
        *,
        validator: RuleRegistryValidatorType = RuleRegistryValidatorType.LLM,
        criteria: list[str] | None = None,
        priority: int = 50,
        scope: str = "draft",
        claim_ids: list[str] | None = None,
        contract_refs: list[str] | None = None,
    ) -> RuleRegistryRule:
        return RuleRegistryRule(
            id=item_id,
            source=source,
            scope=scope,
            category=category,
            title=str(title or category),
            statement=str(statement or ""),
            priority=priority,
            severity=severity,
            binding=RuleBinding(
                validator_type=validator,
                observable_criteria=criteria or [f"Draft satisfies {title or category}."],
                repair_policy="revise" if severity != RuleRegistrySeverity.WARNING else "flag",
            ),
            claim_ids=claim_ids or [],
            contract_refs=contract_refs or [],
        )

    @staticmethod
    def iter_rule_items(value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []
        return [item if isinstance(item, dict) else {"value": item} for item in value]

    @staticmethod
    def as_dict(value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    @staticmethod
    def as_list(value: Any) -> list[Any]:
        return value if isinstance(value, list) else []

    @staticmethod
    def as_list_of_dicts(value: Any) -> list[dict[str, Any]]:
        return [item for item in as_list(value) if isinstance(item, dict)]

publisher_rule_registry = RuleRegistrySectionsComponent.publisher_rule_registry
topic_fabula_registry = RuleRegistrySectionsComponent.topic_fabula_registry
direct_context_registry = RuleRegistrySectionsComponent.direct_context_registry
ledger_registry = RuleRegistrySectionsComponent.ledger_registry
brief_intent_registry = RuleRegistrySectionsComponent.brief_intent_registry
registry_rule = RuleRegistrySectionsComponent.registry_rule
iter_rule_items = RuleRegistrySectionsComponent.iter_rule_items
as_dict = RuleRegistrySectionsComponent.as_dict
as_list = RuleRegistrySectionsComponent.as_list
as_list_of_dicts = RuleRegistrySectionsComponent.as_list_of_dicts


__all__ = (
    'HARD_PUBLISHER_GROUPS',
    'publisher_rule_registry',
    'topic_fabula_registry',
    'direct_context_registry',
    'ledger_registry',
    'brief_intent_registry',
    'registry_rule',
    'iter_rule_items',
    'as_dict',
    'as_list',
    'as_list_of_dicts',
    'RuleRegistrySectionsComponent',
)
