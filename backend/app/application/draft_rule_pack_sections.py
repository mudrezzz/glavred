from typing import Any

from backend.app.domain.draft_rule_pack import RulePackRequirement, RulePackRule

HARD_PUBLISHER_GROUPS = {"antiAiPattern", "forbiddenTopic", "forbiddenTopics", "positioning"}


def publisher_constraints(
    publisher_rules: dict[str, Any],
) -> tuple[list[RulePackRule], list[RulePackRule]]:
    hard: list[RulePackRule] = []
    soft: list[RulePackRule] = []
    for group, rules in as_dict(publisher_rules.get("groups")).items():
        for index, rule in enumerate(iter_rule_items(rules)):
            target = hard if group in HARD_PUBLISHER_GROUPS else soft
            target.append(
                rule_item(
                    f"publisher-{group}-{index}",
                    str(rule.get("title") or group),
                    rule.get("statement") or rule.get("value"),
                    f"publisherRules.{group}",
                    category="hardConstraints" if target is hard else "softConstraints",
                    severity="hard" if target is hard else "soft",
                )
            )
    return hard, soft


def candidate_constraints(candidate: dict[str, Any]) -> list[RulePackRule]:
    fields = [("thesis", "Candidate thesis"), ("value", "Candidate value"), ("goal", "Candidate goal")]
    return [rule_item(f"candidate-{key}", title, candidate[key], "candidate") for key, title in fields if candidate.get(key)]


def evidence_requirements(
    brief: dict[str, Any],
    candidate: dict[str, Any],
    signal: dict[str, Any],
    fabula: dict[str, Any],
) -> list[RulePackRequirement]:
    requirements = [
        requirement_item("brief-evidence", "Brief evidence", brief.get("evidenceCount"), "brief"),
        requirement_item("candidate-evidence", "Candidate evidence", candidate.get("evidenceSummary"), "candidate"),
        requirement_item("signal-summary", "Signal grounding", signal.get("summary"), "sourceSignal"),
        requirement_item("signal-raw-note", "Signal raw note", signal.get("rawNote"), "sourceSignal"),
    ]
    requirements.extend(
        requirement_item(f"fabula-proof-{index}", "Fabula proof", item, "fabula")
        for index, item in enumerate(as_list(fabula.get("proofRequirements")))
    )
    return [item for item in requirements if item.detail]


def dramaturgy_requirements(fabula: dict[str, Any]) -> list[RulePackRequirement]:
    requirements = [
        requirement_item(
            "fabula-dramaturgy", "Fabula dramaturgy", fabula.get("dramaturgy"), "fabula", "dramaturgyRequirements"
        )
    ]
    requirements.extend(
        requirement_item(
            f"fabula-structure-{index}", "Fabula structure", item, "fabula", "dramaturgyRequirements"
        )
        for index, item in enumerate(as_list(fabula.get("structure")))
    )
    return [item for item in requirements if item.detail]


def topic_fit_requirements(topic: dict[str, Any]) -> list[RulePackRequirement]:
    fields = [
        ("topic-purpose", "Topic purpose", topic.get("purpose")),
        ("topic-audience-value", "Audience value", topic.get("audienceValue")),
        ("topic-author-stance", "Author stance", topic.get("authorStance")),
    ]
    requirements = [requirement_item(item_id, title, detail, "topic", "topicFitRequirements") for item_id, title, detail in fields]
    requirements.extend(
        requirement_item(f"topic-rule-{index}", "Topic rule", item, "topic", "topicFitRequirements")
        for index, item in enumerate(as_list(topic.get("rules")))
    )
    return [item for item in requirements if item.detail]


def forbidden_moves(
    topic: dict[str, Any],
    publisher_rules: dict[str, Any],
    candidate: dict[str, Any],
) -> list[RulePackRule]:
    moves = [
        rule_item(f"topic-forbidden-{index}", "Forbidden angle", item, "topic", category="forbiddenMoves")
        for index, item in enumerate(as_list(topic.get("forbiddenAngles")))
    ]
    moves.extend(
        rule_item(f"candidate-risk-{index}", "Candidate risk", item, "candidate", category="forbiddenMoves")
        for index, item in enumerate(as_list(candidate.get("risks")))
    )
    for group in ("forbiddenTopic", "forbiddenTopics"):
        for index, rule in enumerate(iter_rule_items(as_dict(publisher_rules.get("groups")).get(group))):
            moves.append(
                rule_item(
                    f"publisher-{group}-{index}",
                    str(rule.get("title") or "Forbidden topic"),
                    rule.get("statement") or rule.get("value"),
                    f"publisherRules.{group}",
                    category="forbiddenMoves",
                )
            )
    return [item for item in moves if item.statement]


def quality_rubric() -> list[RulePackRequirement]:
    items = [
        ("quality-hard-constraints", "Hard constraints", "No hard constraint is violated."),
        ("quality-evidence", "Evidence grounding", "Claims are grounded in available evidence."),
        ("quality-topic-fit", "Topic fit", "Draft matches topic purpose and audience value."),
        ("quality-fabula-fit", "Fabula fit", "Draft follows the selected dramaturgy."),
    ]
    return [requirement_item(item_id, title, detail, "rulePack", "qualityRubric") for item_id, title, detail in items]


def rule_item(
    item_id: str,
    title: str,
    statement: Any,
    source: str,
    *,
    category: str = "hardConstraints",
    severity: str = "hard",
) -> RulePackRule:
    return RulePackRule(
        id=item_id, category=category, title=title, statement=str(statement or ""), source=source, severity=severity
    )


def requirement_item(
    item_id: str,
    title: str,
    detail: Any,
    source: str,
    category: str = "evidenceRequirements",
) -> RulePackRequirement:
    return RulePackRequirement(id=item_id, category=category, title=title, detail=str(detail or ""), source=source)


def iter_rule_items(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item if isinstance(item, dict) else {"value": item} for item in value]


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def as_list_of_dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in as_list(value) if isinstance(item, dict)]
