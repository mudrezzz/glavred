"""Owner: drafting.application.revision

Used by: DraftRun revision package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

PAIRWISE_RANKING_KEYS = {"winnerCandidateId", "comparisons", "reason"}
PAIRWISE_RANKING_TEMPERATURE = 0.1


class PairwiseRankingPromptBuilder:
    """Owns pairwise ranking provider message construction."""

    def build_from_provider_input(
        self,
        *,
        provider_input: dict[str, Any],
        repair_context: dict[str, Any] | None = None,
    ) -> list[dict[str, str]]:
        payload = {
            "task": "Rank all draft candidates pairwise and select one winner.",
            "requiredJson": self._required_json(),
            "candidates": provider_input.get("candidates"),
            "validationIssues": provider_input.get("validationIssues"),
            "postContract": provider_input.get("postContract"),
            "evidence": provider_input.get("evidence"),
            "selectionConstraints": provider_input.get("selectionConstraints"),
            "repairContext": repair_context,
            "editorialDimensions": provider_input.get("editorialDimensions"),
        }
        return self._messages(payload)

    def build_messages(
        self,
        *,
        draft_artifact: dict[str, Any],
        validation_report: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        context_pack: dict[str, Any] | None = None,
        repair_context: dict[str, Any] | None = None,
    ) -> list[dict[str, str]]:
        payload = {
            "task": "Rank all draft candidates pairwise and select one winner.",
            "requiredJson": self._required_json(),
            "candidates": draft_artifact.get("candidates"),
            "legacySelection": draft_artifact.get("selection"),
            "validationReport": validation_report,
            "postContract": context_artifact.get("postContract"),
            "ruleRegistry": rule_pack.get("ruleRegistrySnapshot"),
            "contextPack": context_pack or {},
            "materialPlan": material_plan,
            "repairContext": repair_context,
            "editorialDimensions": ["ideaStrength", "tension", "readerValue", "authorStance", "sourceIntegration", "structure", "validatorHealth"],
        }
        return self._messages(payload)

    def _required_json(self) -> dict[str, str]:
        return {
            "winnerCandidateId": "candidate id",
            "reason": "short explanation",
            "comparisons": "array of pairwise decisions with decisiveFactors and optional editorialDimensionScores",
            "editorialDimensionScores": "array: dimension, winnerCandidateId, reason",
        }

    def _messages(self, payload: dict[str, Any]) -> list[dict[str, str]]:
        system = (
            "You are Glavred's pairwise draft ranker. Return strict JSON only. "
            "Choose the candidate that best preserves the post contract, source grounding, "
            "publisher rules, validation feedback, and explicit editorial improvement dimensions. "
            "Do not rewrite text."
        )
        return [{"role": "system", "content": system}, {"role": "user", "content": _json(payload)}]


def _json(value: Any) -> str:
    import json

    return json.dumps(value, ensure_ascii=False)
