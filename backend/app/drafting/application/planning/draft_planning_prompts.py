"""Owner: drafting.application.planning

Used by: DraftRun planning migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any


class DraftPlanningPromptsComponent:
    """Owns migrated helper behavior; module-level aliases remain compatibility-only."""

    @staticmethod
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
                    "all projected evidence, explain concrete reasons in rejectedEvidence and rejectionReasons. "
                    "Prefer evidenceInterpretation implications, usable examples, limits, and forbidden overclaims "
                    "over raw citation snippets when they are present."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Context summary:\n{context_summary}\n\n"
                    f"RulePack:\n{rule_pack}\n\n"
                    f"Context pack:\n{context_pack or {}}\n\n"
                    f"Evidence interpretation:\n{rule_pack.get('evidenceInterpretation') or {}}\n\n"
                    f"Usable evidence candidates:\n{usable_evidence_candidates or []}"
                    f"{repair_instruction}"
                ),
            },
        ]

    @staticmethod
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

build_material_plan_messages = DraftPlanningPromptsComponent.build_material_plan_messages
build_draft_strategy_messages = DraftPlanningPromptsComponent.build_draft_strategy_messages


__all__ = (
    'build_material_plan_messages',
    'build_draft_strategy_messages',
    'DraftPlanningPromptsComponent',
)
