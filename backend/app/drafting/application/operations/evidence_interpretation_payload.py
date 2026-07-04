"""Owner: drafting.application.operations

Used by: legacy EvidenceInterpretationService before provider JSON attempts.
Does not own: provider adapters, prompt text, retry policy, rule compilation.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


MAX_RULES = 40
MAX_EXTERNAL_CLAIMS = 24
MAX_PUBLIC_EVIDENCE_ITEMS = 24
MAX_SYNTHESIS_CLAIMS = 24
MAX_WARNINGS = 12


@dataclass(frozen=True)
class EvidenceInterpretationInput:
    context_artifact: dict[str, Any]
    rule_pack: dict[str, Any]
    input_stats: dict[str, Any]


class EvidenceInterpretationPayloadCompactor:
    def compact(
        self,
        *,
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        timeout_seconds: int,
    ) -> EvidenceInterpretationInput:
        rules = _records(_record(rule_pack.get("ruleRegistrySnapshot")).get("rules"))
        compact_rules = _compact_rules(rules)
        source_ledger = _compact_source_ledger(_record(context_artifact.get("sourceLedger")))
        public_evidence = _compact_public_evidence(_record(context_artifact.get("publicEvidence")))
        evidence_synthesis = _compact_evidence_synthesis(_record(context_artifact.get("evidenceSynthesis")))
        compact_context = {
            "postContract": context_artifact.get("postContract"),
            "sourceLedger": source_ledger,
            "publicEvidence": public_evidence,
            "evidenceSynthesis": evidence_synthesis,
        }
        compact_rule_pack = {
            **{key: value for key, value in rule_pack.items() if key != "ruleRegistrySnapshot"},
            "ruleRegistrySnapshot": {
                **{key: value for key, value in _record(rule_pack.get("ruleRegistrySnapshot")).items() if key != "rules"},
                "rules": compact_rules,
                "metadata": {
                    **_record(_record(rule_pack.get("ruleRegistrySnapshot")).get("metadata")),
                    "compactedForEvidenceInterpretation": True,
                    "originalRuleCount": len(rules),
                    "compactRuleCount": len(compact_rules),
                },
            },
        }
        prompt_estimate = len(json.dumps({
            "contextArtifact": compact_context,
            "rulePack": compact_rule_pack,
        }, ensure_ascii=False))
        return EvidenceInterpretationInput(
            context_artifact=compact_context,
            rule_pack=compact_rule_pack,
            input_stats={
                "originalRuleCount": len(rules),
                "compactRuleCount": len(compact_rules),
                "externalClaimCount": len(_records(source_ledger.get("claims"))),
                "publicEvidenceItemCount": len(_records(public_evidence.get("items"))),
                "evidenceSynthesisClaimCount": len(_records(evidence_synthesis.get("externalClaims"))),
                "promptCharEstimate": prompt_estimate,
                "timeoutSeconds": timeout_seconds,
            },
        )


def _compact_rules(rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for rule in rules:
        if _is_relevant_rule(rule):
            selected.append(_compact_rule(rule))
        if len(selected) >= MAX_RULES:
            break
    if selected:
        return selected
    return [_compact_rule(rule) for rule in rules[: min(len(rules), MAX_RULES)]]


def _is_relevant_rule(rule: dict[str, Any]) -> bool:
    severity = str(rule.get("severity") or rule.get("priority") or "").lower()
    searchable = " ".join(
        str(rule.get(key) or "")
        for key in ("id", "title", "scope", "category", "group", "validatorType", "validator", "source")
    ).lower()
    return severity in {"hard", "critical"} or any(
        marker in searchable
        for marker in ("evidence", "source", "attribution", "style", "topic", "fabula", "claim", "ledger")
    )


def _compact_rule(rule: dict[str, Any]) -> dict[str, Any]:
    return _pick(rule, (
        "id",
        "title",
        "scope",
        "category",
        "group",
        "severity",
        "priority",
        "validatorType",
        "observableCriteria",
        "repairPolicy",
        "examples",
    ))


def _compact_source_ledger(source_ledger: dict[str, Any]) -> dict[str, Any]:
    claims = [
        _compact_claim(claim)
        for claim in _records(source_ledger.get("claims"))
        if claim.get("type") == "externalEvidenceClaim"
    ][:MAX_EXTERNAL_CLAIMS]
    return {
        "claims": claims,
        "warnings": _records(source_ledger.get("warnings"))[:MAX_WARNINGS],
        "metadata": {
            **_record(source_ledger.get("metadata")),
            "externalClaimCount": len(claims),
        },
    }


def _compact_claim(claim: dict[str, Any]) -> dict[str, Any]:
    return {
        **_pick(claim, ("id", "type", "statement", "allowedUse", "confidence", "risk", "sourceId")),
        "provenance": _pick(_record(claim.get("provenance")), (
            "publicEvidenceItemId",
            "sourceTitle",
            "sourceUrl",
            "sourceLabel",
            "attemptId",
            "snippet",
        )),
    }


def _compact_public_evidence(public_evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "items": [
            _pick(item, ("id", "sourceTitle", "sourceUrl", "snippet", "summary", "allowedUse", "confidence", "attemptId"))
            for item in _records(public_evidence.get("items"))[:MAX_PUBLIC_EVIDENCE_ITEMS]
        ],
        "warnings": _records(public_evidence.get("warnings"))[:MAX_WARNINGS],
        "budget": public_evidence.get("budget") or public_evidence.get("budgetTrace"),
    }


def _compact_evidence_synthesis(evidence_synthesis: dict[str, Any]) -> dict[str, Any]:
    return {
        "externalClaims": [
            _pick(claim, ("id", "statement", "allowedUse", "confidence", "publicEvidenceItemId", "sourceTitle", "sourceUrl"))
            for claim in _records(evidence_synthesis.get("externalClaims"))[:MAX_SYNTHESIS_CLAIMS]
        ],
        "decisions": _records(evidence_synthesis.get("decisions"))[:MAX_SYNTHESIS_CLAIMS],
        "warnings": _records(evidence_synthesis.get("warnings"))[:MAX_WARNINGS],
        "fallbackUsed": evidence_synthesis.get("fallbackUsed"),
    }


def _pick(payload: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    return {key: payload[key] for key in keys if key in payload and payload[key] not in (None, "", [], {})}


def _record(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _records(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []
