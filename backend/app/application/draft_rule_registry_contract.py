from typing import Any

from backend.app.application.draft_rule_registry_sections import (
    as_list,
    as_list_of_dicts,
    registry_rule,
)
from backend.app.application.draft_rule_registry_size import publication_size_registry
from backend.app.domain.draft_rule_registry import RuleRegistrySeverity, RuleRegistryValidatorType


def contract_registry(contract: dict[str, Any]) -> list:
    if contract.get("status") != "created":
        return []
    rules = [
        registry_rule(
            "contract:thesis",
            "hardConstraints",
            "Locked thesis",
            contract.get("thesis"),
            "postContract.thesis",
            RuleRegistrySeverity.HARD,
            priority=1,
            contract_refs=["thesis"],
            scope="postContract",
        ),
        registry_rule(
            "contract:cta",
            "hardConstraints",
            "Required CTA",
            contract.get("cta"),
            "postContract.cta",
            RuleRegistrySeverity.HARD,
            validator=RuleRegistryValidatorType.DETERMINISTIC,
            priority=25,
            contract_refs=["cta"],
            scope="postContract",
        ),
    ]
    rules.extend(_contract_claim_rules(contract))
    rules.extend(_obligation_rules(contract, "evidenceObligations", "evidenceRequirements"))
    rules.extend(_obligation_rules(contract, "fabulaObligations", "dramaturgyRequirements"))
    rules.extend(publication_size_registry(contract))
    rules.extend(
        registry_rule(
            f"contract:forbidden:{index}",
            "forbiddenMoves",
            "Contract forbidden move",
            item,
            "postContract.forbiddenMoves",
            RuleRegistrySeverity.HARD,
            validator=RuleRegistryValidatorType.DETERMINISTIC,
            priority=8,
            scope="postContract",
        )
        for index, item in enumerate(as_list(contract.get("forbiddenMoves")))
    )
    return [rule for rule in rules if rule.statement]


def _contract_claim_rules(contract: dict[str, Any]) -> list:
    rules = []
    for item in as_list_of_dicts(contract.get("claims")):
        claim_id = str(item.get("id") or "")
        if not claim_id:
            continue
        needs_qualification = item.get("allowedUse") == "needsQualification" or item.get("qualification")
        rules.append(
            registry_rule(
                f"contract:claim:{claim_id}",
                "evidenceRequirements",
                "Contract claim",
                f"Use claim {claim_id} as {item.get('allowedUse')}",
                "postContract.claims",
                RuleRegistrySeverity.WARNING if needs_qualification else RuleRegistrySeverity.HARD,
                priority=28,
                claim_ids=[claim_id],
                contract_refs=["claims"],
                scope="postContract",
            )
        )
    return rules


def _obligation_rules(contract: dict[str, Any], key: str, category: str) -> list:
    return [
        registry_rule(
            f"contract:{key}:{item.get('id') or index}",
            category,
            f"Contract {key}",
            item.get("statement"),
            str(item.get("source") or f"postContract.{key}"),
            RuleRegistrySeverity.HARD,
            priority=30,
            contract_refs=[key],
            scope="postContract",
        )
        for index, item in enumerate(as_list_of_dicts(contract.get(key)))
    ]
