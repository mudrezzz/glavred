"""Owner: drafting.application.operations

Used by: Payload budget compactors for rules, ledger claims, and evidence summaries.
Does not own: Draft artifacts, prompt text, provider adapters, or semantic contracts.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from typing import Any

from backend.app.drafting.application.operations.payload_budget_contracts import PayloadBudgetProfile
from backend.app.drafting.application.operations.payload_compactor_common import CountAccumulator, _drop_empty, _pick, _record, _records
from backend.app.drafting.application.operations.payload_record_compactors import EvidenceRecordCompactor


class RulePackCompactor:
    def compact(self, rule_pack: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
        snapshot = _record(rule_pack.get("ruleRegistrySnapshot"))
        rules = _records(snapshot.get("rules"))
        selected = [self._compact_rule(rule) for rule in self._select_rules(rules, profile.max_rules)]
        compact_snapshot = {
            **{key: value for key, value in snapshot.items() if key not in {"rules", "sourceLedger", "fullRuleRegistry"}},
            "rules": selected,
            "metadata": {
                **_record(snapshot.get("metadata")),
                "payloadBudgeted": True,
                "originalRuleCount": len(rules),
                "sentRuleCount": len(selected),
            },
        }
        compact = {
            **{key: value for key, value in rule_pack.items() if key not in {"ruleRegistrySnapshot", "sourceLedger"}},
            "ruleRegistrySnapshot": compact_snapshot,
        }
        trimmed: dict[str, int] = {}
        CountAccumulator.trimmed(trimmed, "rules", len(rules), len(selected))
        return compact, trimmed

    def _select_rules(self, rules: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
        relevant = [rule for rule in rules if self._is_relevant_rule(rule)]
        return relevant[:limit] if relevant else rules[:limit]

    def _is_relevant_rule(self, rule: dict[str, Any]) -> bool:
        severity = str(rule.get("severity") or rule.get("priority") or "").lower()
        searchable = " ".join(str(rule.get(key) or "") for key in ("id", "title", "scope", "category", "group", "validatorType", "source")).lower()
        return severity in {"hard", "critical"} or any(
            marker in searchable
            for marker in ("evidence", "source", "claim", "topic", "fabula", "contract", "attribution")
        )

    def _compact_rule(self, rule: dict[str, Any]) -> dict[str, Any]:
        return _pick(rule, ("id", "title", "scope", "category", "group", "severity", "priority", "validatorType", "observableCriteria", "repairPolicy", "examples"))


class SourceLedgerCompactor:
    def compact(self, source_ledger: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
        claims = _records(source_ledger.get("claims"))
        selected = [EvidenceRecordCompactor.compact_claim(claim) for claim in claims[: profile.max_claims]]
        compact = {
            "claims": selected,
            "warnings": _records(source_ledger.get("warnings"))[: min(8, profile.max_claims)],
            "metadata": {
                **_record(source_ledger.get("metadata")),
                "payloadBudgeted": True,
                "originalClaimCount": len(claims),
                "sentClaimCount": len(selected),
            },
        }
        counts: dict[str, int] = {}
        CountAccumulator.trimmed(counts, "claims", len(claims), len(selected))
        return compact, counts


class PublicEvidenceCompactor:
    def compact(self, public_evidence: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
        items = _records(public_evidence.get("items"))
        selected = [EvidenceRecordCompactor.compact_evidence_item(item) for item in items[: profile.max_evidence_items]]
        counts: dict[str, int] = {}
        CountAccumulator.trimmed(counts, "evidenceItems", len(items), len(selected))
        return _drop_empty({"items": selected, "budget": public_evidence.get("budget") or public_evidence.get("budgetTrace")}), counts


class EvidenceSynthesisCompactor:
    def compact(self, evidence_synthesis: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
        claims = _records(evidence_synthesis.get("externalClaims"))
        selected = [EvidenceRecordCompactor.compact_claim(claim) for claim in claims[: profile.max_claims]]
        counts: dict[str, int] = {}
        CountAccumulator.trimmed(counts, "synthesisClaims", len(claims), len(selected))
        return _drop_empty(
            {
                "externalClaims": selected,
                "decisions": _records(evidence_synthesis.get("decisions"))[: profile.max_claims],
                "warnings": _records(evidence_synthesis.get("warnings"))[: min(8, profile.max_claims)],
                "fallbackUsed": evidence_synthesis.get("fallbackUsed"),
            }
        ), counts
