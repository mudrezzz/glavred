from typing import Any


def build_material_plan_messages(
    *,
    context_summary: dict[str, Any],
    rule_pack: dict[str, Any],
) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You are Glavred material planner. Return strict JSON with keys: "
                "availableEvidence, missingEvidence, riskyClaims, groundingPlan, sourceNotes, openQuestions."
            ),
        },
        {
            "role": "user",
            "content": f"Context summary:\n{context_summary}\n\nRulePack:\n{rule_pack}",
        },
    ]


def build_draft_strategy_messages(
    *,
    context_summary: dict[str, Any],
    rule_pack: dict[str, Any],
    material_plan: dict[str, Any],
) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You are Glavred draft strategist. Return strict JSON with keys: "
                "thesisAngle, openingMove, argumentSequence, fabulaUsage, ctaPlan, "
                "forbiddenMoves, toneNotes."
            ),
        },
        {
            "role": "user",
            "content": f"Context summary:\n{context_summary}\n\nRulePack:\n{rule_pack}\n\nMaterial plan:\n{material_plan}",
        },
    ]
