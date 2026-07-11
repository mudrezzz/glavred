"""Owner: drafting.application.generation

Used by: DraftRun generation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

import json
from typing import Any

from backend.app.domain.draft_candidates import DraftCandidateDirection

CANDIDATE_TEMPERATURE = 0.55
CANDIDATE_KEYS = {"title", "body", "rationale", "usedEvidence", "ruleCoverage", "risks", "weaknesses"}


class DraftCandidatePromptBuilder:
    SYSTEM_MESSAGE = (
        "You are Glavred's draft-writing agent. Return only valid JSON with keys: "
        "title, body, rationale, usedEvidence, ruleCoverage, risks, weaknesses. "
        "The draft must obey hard constraints and stay grounded in evidence. "
        "Use evidenceInterpretation implications, examples, limits, and forbidden overclaims "
        "when present; do not paste raw citations as decoration. "
        "Do not mechanically expose internal pipeline artifact names as dev-jargon, such as SourceLedger, "
        "publicEvidence, validators, RuleRegistry, or PostContract in public prose. "
        "Use them only if you intentionally frame and explain them as reader-facing concepts."
    )

    def build_from_provider_input(
        self,
        *,
        provider_input: dict[str, Any],
        repair_context: dict[str, Any] | None = None,
    ) -> list[dict[str, str]]:
        return self._messages(
            {
                "providerInput": provider_input,
                "repairContext": repair_context,
                "outputLanguage": "ru",
            }
        )

    def build_legacy(
        self,
        *,
        context_summary: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        draft_strategy: dict[str, Any],
        direction: DraftCandidateDirection,
        context_pack: dict[str, Any] | None = None,
        repair_context: dict[str, Any] | None = None,
    ) -> list[dict[str, str]]:
        return self._messages(
            {
                "direction": direction.to_payload(),
                "contextSummary": context_summary,
                "rulePack": rule_pack,
                "materialPlan": material_plan,
                "draftStrategy": draft_strategy,
                "contextPack": context_pack or {},
                "repairContext": repair_context,
                "outputLanguage": "ru",
            }
        )

    def _messages(self, payload: dict[str, Any]) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": self.SYSTEM_MESSAGE},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ]


def build_draft_candidate_messages(
    *,
    context_summary: dict[str, Any],
    rule_pack: dict[str, Any],
    material_plan: dict[str, Any],
    draft_strategy: dict[str, Any],
    direction: DraftCandidateDirection,
    context_pack: dict[str, Any] | None = None,
    repair_context: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    return DraftCandidatePromptBuilder().build_legacy(
        context_summary=context_summary,
        rule_pack=rule_pack,
        material_plan=material_plan,
        draft_strategy=draft_strategy,
        direction=direction,
        context_pack=context_pack,
        repair_context=repair_context,
    )
