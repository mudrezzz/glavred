import json
from typing import Any


EVIDENCE_INTERPRETATION_KEYS = {
    "implications",
    "tensions",
    "usableExamples",
    "limits",
    "forbiddenOverclaims",
    "authorPositionLinks",
    "readerValueHooks",
    "recommendedUseByPlan",
    "rejectedEvidenceUses",
    "warnings",
}
EVIDENCE_INTERPRETATION_TEMPERATURE = 0.2


def build_evidence_interpretation_messages(
    *,
    context_summary: dict[str, Any],
    context_artifact: dict[str, Any],
    rule_pack: dict[str, Any],
    context_pack: dict[str, Any] | None = None,
    repair_context: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    repair = {}
    if repair_context:
        repair = {
            "repairContext": repair_context,
            "repairInstruction": (
                "Return only the required JSON object. Keep every item tied to sourceIds, "
                "publicEvidenceItemIds, claimIds, and ruleIds when available."
            ),
        }
    return [
        {
            "role": "system",
            "content": (
                "You are Glavred's evidence interpretation strategist. Return strict JSON only. "
                "Do not write prose. Do not invent facts. Do not create a new thesis or new angle. "
                "Interpret accepted public evidence inside the approved PostContract, RuleRegistry, "
                "topic/fabula rules, publisher rules, and author-position constraints. "
                "Required keys: implications, tensions, usableExamples, limits, forbiddenOverclaims, "
                "authorPositionLinks, readerValueHooks, recommendedUseByPlan, rejectedEvidenceUses, warnings. "
                "Each array item should include id, title, summary, sourceIds, publicEvidenceItemIds, "
                "claimIds, ruleIds, contractObligationIds, confidence, allowedUse, reason."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {
                    "contextSummary": context_summary,
                    "postContract": context_artifact.get("postContract"),
                    "sourceLedger": context_artifact.get("sourceLedger"),
                    "publicEvidence": context_artifact.get("publicEvidence"),
                    "evidenceSynthesis": context_artifact.get("evidenceSynthesis"),
                    "ruleRegistrySnapshot": rule_pack.get("ruleRegistrySnapshot"),
                    "contextPack": context_pack or {},
                    **repair,
                },
                ensure_ascii=False,
            ),
        },
    ]
