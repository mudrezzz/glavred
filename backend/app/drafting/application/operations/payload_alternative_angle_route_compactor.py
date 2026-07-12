"""Owner: drafting.application.operations

Used by: provider-input budgeting for the alternative-angle route operation.
Does not own: record projection, prompt wording, provider calls, or tournament policy.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Callable

from backend.app.drafting.application.operations.alternative_angle_route_projection import AlternativeAngleRouteProjection
from backend.app.drafting.application.operations.payload_budget_contracts import PayloadBudgetProfile


class AlternativeAngleRoutePayloadCompactor:
    """Selects route evidence fairly and enforces the total dossier budget."""

    BASE_DOSSIER_CHAR_LIMIT = 18_500
    REPAIR_CONTEXT_CHAR_LIMIT = 1_500

    def __init__(self) -> None:
        self._projection = AlternativeAngleRouteProjection()

    def compact(self, payload: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
        if profile.operation_id != "alternativeAngleRoute" or "dossierId" not in payload:
            return payload, {}
        compact = dict(payload)
        trimmed: dict[str, int] = {}
        candidates = self._records(compact.get("candidates"))[:3]
        candidate_ids = [self._projection.text(item.get("id"), 120) for item in candidates]
        compact["candidates"] = [self._projection.candidate(item) for item in candidates]
        self._count(trimmed, "candidates", len(self._records(payload.get("candidates"))), len(candidates))
        self._count_chars(trimmed, "candidatesChars", payload.get("candidates"), compact["candidates"])

        compact["critiqueSignals"] = self._candidate_scoped(
            compact.get("critiqueSignals"), candidate_ids, self._projection.critique, "critiqueSignals", trimmed
        )
        compact["validationIssues"] = self._candidate_scoped(
            compact.get("validationIssues"), candidate_ids, self._projection.validation_issue, "validationIssues", trimmed
        )
        compact["rejectedMoves"] = self._mapped(
            compact.get("rejectedMoves"), 2, self._projection.rejected_move, "rejectedMoves", trimmed
        )
        compact["evidence"] = self._mapped(compact.get("evidence"), 2, self._projection.evidence, "evidence", trimmed)
        compact["rules"] = self._mapped(compact.get("rules"), 2, self._projection.rule, "rules", trimmed)
        compact["postContract"] = self._projection.post_contract(compact.get("postContract"))
        if "repairContext" in compact:
            compact["repairContext"] = self._projection.repair_context(compact.get("repairContext"))

        for key in ("critiqueSignals", "validationIssues", "rejectedMoves", "evidence", "rules", "postContract", "repairContext"):
            if key in compact:
                self._count_chars(trimmed, f"{key}Chars", payload.get(key), compact[key])
        compact = {key: value for key, value in compact.items() if value not in (None, [], {})}
        return self._fit_total(compact, trimmed), trimmed

    def _candidate_scoped(
        self,
        value: Any,
        candidate_ids: list[str],
        mapper: Callable[[Mapping[str, Any]], dict[str, Any]],
        key: str,
        trimmed: dict[str, int],
    ) -> list[dict[str, Any]]:
        records = self._prioritized(value)
        selected = []
        for candidate_id in candidate_ids:
            match = next((item for item in records if self._projection.text(item.get("candidateId"), 120) == candidate_id), None)
            if match is not None:
                selected.append(match)
        for item in records:
            if len(selected) >= 3:
                break
            if item not in selected:
                selected.append(item)
        self._count(trimmed, key, len(records), len(selected))
        return [mapper(item) for item in selected]

    def _mapped(
        self,
        value: Any,
        limit: int,
        mapper: Callable[[Mapping[str, Any]], dict[str, Any]],
        key: str,
        trimmed: dict[str, int],
    ) -> list[dict[str, Any]]:
        records = self._prioritized(value)
        selected = records[:limit]
        self._count(trimmed, key, len(records), len(selected))
        return [mapper(item) for item in selected]

    def _prioritized(self, value: Any) -> list[dict[str, Any]]:
        severity = {"critical": 0, "error": 0, "warning": 1, "observation": 2, "info": 3}
        return sorted(self._records(value), key=lambda item: (
            severity.get(self._projection.text(item.get("severity") or item.get("status"), 24).lower(), 4),
            self._projection.text(item.get("candidateId"), 120),
            self._projection.text(item.get("validatorId") or item.get("id"), 120),
        ))

    def _fit_total(self, payload: dict[str, Any], trimmed: dict[str, int]) -> dict[str, Any]:
        limit = self.BASE_DOSSIER_CHAR_LIMIT + (self.REPAIR_CONTEXT_CHAR_LIMIT if payload.get("repairContext") else 0)
        for key in ("rules", "evidence", "rejectedMoves", "validationIssues"):
            while self._projection.chars(payload) > limit and len(payload.get(key, [])) > 1:
                payload[key] = payload[key][:-1]
                trimmed[key] = trimmed.get(key, 0) + 1
        return payload

    def _records(self, value: Any) -> list[dict[str, Any]]:
        return self._projection.records(value)

    def _count(self, trimmed: dict[str, int], key: str, total: int, sent: int) -> None:
        if total > sent:
            trimmed[key] = trimmed.get(key, 0) + total - sent

    def _count_chars(self, trimmed: dict[str, int], key: str, source: Any, sent: Any) -> None:
        removed = max(0, self._projection.chars(source) - self._projection.chars(sent))
        if removed:
            trimmed[key] = trimmed.get(key, 0) + removed


__all__ = ("AlternativeAngleRoutePayloadCompactor",)
