"""Owner: drafting.application.revision

Used by: DraftRun revision package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.revision.pairwise_comparison_identity import (
    EDITORIAL_DIMENSIONS,
    PairwiseComparisonIdentityPolicy,
)

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
        candidate_ids = self._candidate_ids(provider_input.get("candidates"))
        payload = {
            "task": "Rank all draft candidates pairwise and select one winner.",
            "requiredJson": self._required_json(),
            "comparisonContract": self._comparison_contract(candidate_ids),
            "candidates": provider_input.get("candidates"),
            "validationIssues": provider_input.get("validationIssues"),
            "postContract": provider_input.get("postContract"),
            "evidence": provider_input.get("evidence"),
            "selectionConstraints": provider_input.get("selectionConstraints"),
            "repairContext": repair_context,
            "editorialDimensions": list(EDITORIAL_DIMENSIONS),
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
            "comparisonContract": self._comparison_contract(self._candidate_ids(draft_artifact.get("candidates"))),
            "candidates": draft_artifact.get("candidates"),
            "legacySelection": draft_artifact.get("selection"),
            "validationReport": validation_report,
            "postContract": context_artifact.get("postContract"),
            "ruleRegistry": rule_pack.get("ruleRegistrySnapshot"),
            "contextPack": context_pack or {},
            "materialPlan": material_plan,
            "repairContext": repair_context,
            "editorialDimensions": list(EDITORIAL_DIMENSIONS),
        }
        return self._messages(payload)

    def _required_json(self) -> dict[str, Any]:
        return {
            "winnerCandidateId": "candidate id",
            "reason": "short explanation",
            "comparisons": [{
                "leftCandidateId": "exact candidate id from comparisonContract",
                "rightCandidateId": "exact candidate id from comparisonContract",
                "winnerCandidateId": "one of leftCandidateId or rightCandidateId",
                "reason": "non-empty comparison reason",
                "decisiveFactors": ["specific factor"],
            }],
            "editorialDimensionScores": [{
                "dimension": "one exact editorialDimensions value, each exactly once",
                "winnerCandidateId": "known candidate id",
                "reason": "non-empty dimension reason",
            }],
        }

    def _comparison_contract(self, candidate_ids: list[str]) -> dict[str, Any]:
        pairs = PairwiseComparisonIdentityPolicy().expected_pairs(candidate_ids)
        return {
            "candidateIds": candidate_ids,
            "expectedPairCount": len(pairs),
            "expectedPairs": [{"leftCandidateId": left, "rightCandidateId": right} for left, right in pairs],
            "rules": [
                "Return every expected unordered pair exactly once.",
                "Do not omit, duplicate, reverse-duplicate, or invent a pair.",
                "Never infer candidate identity from response position.",
            ],
        }

    def _candidate_ids(self, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item.get("id")) for item in value if isinstance(item, dict) and item.get("id")]

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
