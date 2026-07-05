"""Owner: drafting.application.evidence

Used by: DraftRun evidence migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.evidence.draft_rule_registry_contract import contract_registry
from backend.app.drafting.application.evidence.draft_rule_registry_sections import (
    as_dict,
    as_list_of_dicts,
    brief_intent_registry,
    direct_context_registry,
    ledger_registry,
    publisher_rule_registry,
    topic_fabula_registry,
)
from backend.app.domain.draft_rule_registry import RuleRegistrySnapshot


class DraftRuleRegistryCompiler:
    def compile(self, context_artifact: dict[str, Any]) -> RuleRegistrySnapshot:
        brief = as_dict(context_artifact.get("brief"))
        candidate = as_dict(context_artifact.get("candidate"))
        signal = as_dict(context_artifact.get("sourceSignal"))
        topic = as_dict(context_artifact.get("topic"))
        fabula = as_dict(context_artifact.get("fabula"))
        publisher_rules = as_dict(context_artifact.get("publisherRules"))
        ledger = as_dict(context_artifact.get("sourceLedger"))
        ledger_metadata = as_dict(ledger.get("metadata"))
        feasibility = as_dict(context_artifact.get("feasibilityReport"))
        post_contract = as_dict(context_artifact.get("postContract"))
        missing_context = as_list_of_dicts(context_artifact.get("missingContext"))
        warnings = [*missing_context, *as_list_of_dicts(ledger.get("warnings"))]

        rules = [
            *brief_intent_registry(brief),
            *publisher_rule_registry(publisher_rules),
            *topic_fabula_registry(topic, fabula),
            *direct_context_registry(candidate, signal),
            *ledger_registry(ledger),
            *contract_registry(post_contract),
        ]

        return RuleRegistrySnapshot(
            rules=rules,
            warnings=warnings,
            metadata={
                "source": "context-sourceLedger-feasibility-postContract",
                "briefOnly": bool(context_artifact.get("compatibility", {}).get("briefOnly")),
                "missingContextCount": len(missing_context),
                "sourceLedgerClaimCount": ledger_metadata.get("claimCount", 0),
                "sourceLedgerWarningCount": ledger_metadata.get("warningCount", 0),
                "feasibilityStatus": feasibility.get("status"),
                "postContractStatus": post_contract.get("status"),
            },
        )


__all__ = (
    'DraftRuleRegistryCompiler',
    'RuleRegistryCompilerComponent',
)
