"""Owner: drafting.application.operations

Used by: Review dossier payload compaction for final-quality sections.
Does not own: candidate projection, provider calls, prompts, or gate decisions.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class FinalQualityDossierSectionCompactor:
    def compact(self, payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, int]]:
        compact = dict(payload)
        trimmed: dict[str, int] = {}
        self._replace(compact, "finalQualityContract", self._contract(compact.get("finalQualityContract"), trimmed))
        self._replace(compact, "deterministicGate", self._gate(compact.get("deterministicGate"), trimmed))
        self._replace(compact, "repairHistory", self._history(compact.get("repairHistory"), trimmed))
        self._replace(compact, "finalQualityIssues", self._issues(compact.get("finalQualityIssues"), trimmed))
        return compact, trimmed

    def _contract(self, value: Any, trimmed: dict[str, int]) -> dict[str, Any]:
        contract = self._mapping(value)
        result = self._pick(contract, ("version", "researchDepth", "publicationKind", "fabulaSizeIntent", "thesis", "audience", "cta", "sourceIntegrationPolicy", "authorVoicePolicy", "examplePolicy"))
        for key, limit in (
            ("forbiddenPublicTerms", 10),
            ("sourceAttributionRequired", 10),
            ("qualifiedClaimIds", 10),
            ("hardRuleIds", 16),
            ("acceptanceCriteria", 8),
        ):
            result[key] = self._bounded_list(contract.get(key), limit, 320, f"finalQualityContract.{key}", trimmed)
        result["unresolvedAttributionRequirements"] = self._bounded(contract.get("unresolvedAttributionRequirements"), 4, 280)
        return self._drop_empty(result)

    def _gate(self, value: Any, trimmed: dict[str, int]) -> dict[str, Any]:
        gate = self._mapping(value)
        result = self._pick(gate, ("status", "candidateId", "finalDraftStatus", "publicProseStatus", "sourceIntegrationStatus", "internalJargonLeaks", "sourceDumpRisk", "authorVoiceStrength", "readerValueClarity", "revisionLoopStopReason"))
        result["finalRepairGoals"] = self._bounded_list(gate.get("finalRepairGoals"), 6, 360, "deterministicGate.finalRepairGoals", trimmed)
        findings = self._records(gate.get("actionableAttributionFindings"))
        selected = findings[:5]
        self._count(trimmed, "deterministicGate.actionableAttributionFindings", len(findings), len(selected))
        result["actionableAttributionFindings"] = [self._issue(item) for item in selected]
        return self._drop_empty(result)

    def _history(self, value: Any, trimmed: dict[str, int]) -> dict[str, Any]:
        history = self._mapping(value)
        cycles = self._records(history.get("cycles"))
        selected = cycles[-3:]
        self._count(trimmed, "repairHistory.cycles", len(cycles), len(selected))
        return self._drop_empty({
            **self._pick(history, ("status", "stopReason")),
            "cycles": [self._pick(item, ("cycle", "status", "candidateId", "winnerId", "accepted", "reason")) for item in selected],
        })

    def _issues(self, value: Any, trimmed: dict[str, int]) -> dict[str, Any]:
        lifecycle = self._mapping(value)
        items = self._records(lifecycle.get("items"))
        selected = items[:6]
        self._count(trimmed, "finalQualityIssues.items", len(items), len(selected))
        return self._drop_empty({
            **self._pick(lifecycle, ("status", "overallVerdict")),
            "items": [self._issue(item) for item in selected],
        })

    def _issue(self, value: Mapping[str, Any]) -> dict[str, Any]:
        return self._drop_empty({
            **self._pick(value, ("id", "candidateId", "source", "validatorId", "severity")),
            "message": self._text(value.get("message"), 240),
            "repairGuidance": self._text(value.get("repairGuidance"), 240),
            "evidenceExcerpt": self._text(value.get("evidenceExcerpt"), 180),
        })

    def _bounded_list(self, value: Any, limit: int, text_limit: int, key: str, trimmed: dict[str, int]) -> list[Any]:
        items = list(value) if isinstance(value, list) else []
        selected = items[:limit]
        self._count(trimmed, key, len(items), len(selected))
        return [self._bounded(item, 8, text_limit) for item in selected]

    def _bounded(self, value: Any, list_limit: int, text_limit: int) -> Any:
        if isinstance(value, str):
            return self._text(value, text_limit)
        if isinstance(value, Mapping):
            return {str(key): self._bounded(child, list_limit, text_limit) for key, child in list(value.items())[:12]}
        if isinstance(value, list):
            return [self._bounded(child, list_limit, text_limit) for child in value[:list_limit]]
        return value

    def _replace(self, payload: dict[str, Any], key: str, value: Any) -> None:
        if key in payload:
            payload[key] = value

    def _mapping(self, value: Any) -> Mapping[str, Any]:
        return value if isinstance(value, Mapping) else {}

    def _records(self, value: Any) -> list[dict[str, Any]]:
        return [dict(item) for item in value if isinstance(item, Mapping)] if isinstance(value, list) else []

    def _pick(self, value: Mapping[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
        return {key: value.get(key) for key in keys if value.get(key) not in (None, [], {})}

    def _drop_empty(self, value: Mapping[str, Any]) -> dict[str, Any]:
        return {key: child for key, child in value.items() if child not in (None, "", [], {})}

    def _text(self, value: Any, limit: int) -> str:
        return str(value or "")[:limit]

    def _count(self, trimmed: dict[str, int], key: str, total: int, sent: int) -> None:
        if total > sent:
            trimmed[key] = total - sent


__all__ = ("FinalQualityDossierSectionCompactor",)
