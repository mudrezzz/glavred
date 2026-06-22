from typing import Any

from backend.app.application.draft_rule_pack_from_registry import requirements_from_registry, rules_from_registry
from backend.app.application.draft_rule_pack_sections import as_dict, as_list_of_dicts, quality_rubric
from backend.app.application.draft_rule_registry_compiler import DraftRuleRegistryCompiler
from backend.app.domain.draft_rule_pack import RulePack


class DraftRulePackCompiler:
    def __init__(self, registry_compiler: DraftRuleRegistryCompiler | None = None) -> None:
        self._registry_compiler = registry_compiler or DraftRuleRegistryCompiler()

    def compile(self, context_summary: dict[str, Any]) -> RulePack:
        brief = as_dict(context_summary.get("brief"))
        missing_context = as_list_of_dicts(context_summary.get("missingContext"))
        source_ledger = as_dict(context_summary.get("sourceLedger"))
        feasibility = as_dict(context_summary.get("feasibilityReport"))
        post_contract = as_dict(context_summary.get("postContract"))
        source_ledger_metadata = as_dict(source_ledger.get("metadata"))
        source_ledger_warnings = as_list_of_dicts(source_ledger.get("warnings"))
        registry_snapshot = self._registry_compiler.compile(context_summary).to_payload()

        return RulePack(
            draft_intent={
                "title": brief.get("title"),
                "thesis": brief.get("thesis"),
                "audience": brief.get("audience"),
                "conflict": brief.get("conflict"),
                "authorPosition": brief.get("authorPosition"),
                "cta": brief.get("cta"),
            },
            hard_constraints=rules_from_registry(registry_snapshot, "hardConstraints"),
            soft_constraints=rules_from_registry(registry_snapshot, "softConstraints"),
            evidence_requirements=requirements_from_registry(registry_snapshot, "evidenceRequirements"),
            dramaturgy_requirements=requirements_from_registry(registry_snapshot, "dramaturgyRequirements"),
            topic_fit_requirements=requirements_from_registry(registry_snapshot, "topicFitRequirements"),
            quality_rubric=quality_rubric(),
            forbidden_moves=rules_from_registry(registry_snapshot, "forbiddenMoves"),
            metadata={
                "version": "rule-pack-v1",
                "registryVersion": registry_snapshot.get("version"),
                "registryRuleCount": registry_snapshot.get("metadata", {}).get("ruleCount", 0),
                "briefOnly": bool(context_summary.get("compatibility", {}).get("briefOnly")),
                "missingContextCount": len(missing_context),
                "sourceLedgerClaimCount": source_ledger_metadata.get("claimCount", 0),
                "sourceLedgerWarningCount": source_ledger_metadata.get("warningCount", 0),
                "feasibilityStatus": feasibility.get("status"),
                "postContractStatus": post_contract.get("status"),
            },
            warnings=[*missing_context, *source_ledger_warnings],
            rule_registry_snapshot=registry_snapshot,
        )
