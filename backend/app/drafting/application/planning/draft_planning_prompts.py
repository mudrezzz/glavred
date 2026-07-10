"""Owner: drafting.application.planning

Used by: DraftRun planning migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

import json
from typing import Any


class DraftPlanningPromptsComponent:
    """Owns migrated helper behavior; module-level aliases remain compatibility-only."""

    @staticmethod
    def build_material_plan_messages(
        *,
        dossier_input: dict[str, Any],
    ) -> list[dict[str, str]]:
        repair_context = dossier_input.get("repairContext")
        repair_instruction = ""
        if isinstance(repair_context, dict) and repair_context:
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
                    "Planning dossier:\n"
                    f"{json.dumps(dossier_input, ensure_ascii=False, sort_keys=True)}"
                    f"{repair_instruction}"
                ),
            },
        ]

    @staticmethod
    def build_draft_strategy_messages(
        *,
        dossier_input: dict[str, Any],
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
                "content": (
                    "Planning dossier:\n"
                    f"{json.dumps(dossier_input, ensure_ascii=False, sort_keys=True)}"
                ),
            },
        ]

build_material_plan_messages = DraftPlanningPromptsComponent.build_material_plan_messages
build_draft_strategy_messages = DraftPlanningPromptsComponent.build_draft_strategy_messages


__all__ = (
    'build_material_plan_messages',
    'build_draft_strategy_messages',
    'DraftPlanningPromptsComponent',
)
