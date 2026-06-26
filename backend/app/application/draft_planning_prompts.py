from typing import Any


def build_material_plan_messages(
    *,
    context_summary: dict[str, Any],
    rule_pack: dict[str, Any],
    usable_evidence_candidates: list[dict[str, Any]] | None = None,
    context_pack: dict[str, Any] | None = None,
    repair_context: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    repair_instruction = ""
    if repair_context:
        repair_instruction = (
            "\n\nRepair context:\n"
            f"{repair_context}\n"
            "The previous answer failed accountability. Either select usable evidence or "
            "explain why each top candidate is rejected."
        )
    return [
        {
            "role": "system",
            "content": (
                "You are Glavred material planner. Return strict JSON with keys: "
                "availableEvidence, rejectedEvidence, rejectionReasons, claimsRequiringAttribution, "
                "qualifiedClaims, missingEvidence, riskyClaims, groundingPlan, sourceNotes, openQuestions. "
                "Use availableEvidence for source-ledger claims that can support the post. If you reject "
                "all projected evidence, explain concrete reasons in rejectedEvidence and rejectionReasons."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Context summary:\n{context_summary}\n\n"
                f"RulePack:\n{rule_pack}\n\n"
                f"Context pack:\n{context_pack or {}}\n\n"
                f"Usable evidence candidates:\n{usable_evidence_candidates or []}"
                f"{repair_instruction}"
            ),
        },
    ]


def build_draft_strategy_messages(
    *,
    context_summary: dict[str, Any],
    rule_pack: dict[str, Any],
    material_plan: dict[str, Any],
    context_pack: dict[str, Any] | None = None,
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
            "content": f"Context summary:\n{context_summary}\n\nRulePack:\n{rule_pack}\n\nContext pack:\n{context_pack or {}}\n\nMaterial plan:\n{material_plan}",
        },
    ]
