from typing import Any

PAIRWISE_RANKING_KEYS = {"winnerCandidateId", "comparisons", "reason"}
PAIRWISE_RANKING_TEMPERATURE = 0.1


def build_pairwise_ranking_messages(
    *,
    draft_artifact: dict[str, Any],
    validation_report: dict[str, Any],
    context_artifact: dict[str, Any],
    rule_pack: dict[str, Any],
    material_plan: dict[str, Any],
    context_pack: dict[str, Any] | None = None,
    repair_context: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    system = (
        "You are Glavred's pairwise draft ranker. Return strict JSON only. "
        "Choose the candidate that best preserves the post contract, source grounding, "
        "publisher rules, and validation feedback. Do not rewrite text."
    )
    payload = {
        "task": "Rank all draft candidates pairwise and select one winner.",
        "requiredJson": {
            "winnerCandidateId": "candidate id",
            "reason": "short explanation",
            "comparisons": [
                {
                    "leftCandidateId": "candidate id",
                    "rightCandidateId": "candidate id",
                    "winnerCandidateId": "candidate id",
                    "reason": "why this candidate wins",
                    "decisiveFactors": ["source grounding", "contract fit"],
                }
            ],
        },
        "candidates": draft_artifact.get("candidates"),
        "legacySelection": draft_artifact.get("selection"),
        "validationReport": validation_report,
        "postContract": context_artifact.get("postContract"),
        "ruleRegistry": rule_pack.get("ruleRegistrySnapshot"),
        "contextPack": context_pack or {},
        "materialPlan": material_plan,
        "repairContext": repair_context,
    }
    return [{"role": "system", "content": system}, {"role": "user", "content": _json(payload)}]


def _json(value: Any) -> str:
    import json

    return json.dumps(value, ensure_ascii=False)
