"""Owner: drafting.application.context

Used by: alternative-angle and writer dossier factories.
Does not own: route selection, prompt construction, provider calls, or persistence.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from backend.app.drafting.application.context.draft_run_artifact_index import DraftRunArtifactIndex
from backend.app.drafting.domain.provider_dossier import ArtifactHandle, ContextSelection


class AlternativeAngleContextReader:
    def __init__(self, index: DraftRunArtifactIndex) -> None:
        self._index = index

    def critique_signals(self, limit: int = 12) -> ContextSelection:
        validation = self._mapping(self._index.step_payload("validation"))
        critique = self._mapping(validation.get("editorialCritiqueReport"))
        reports = self._records(critique.get("candidateReports"))
        selected = reports[: max(0, limit)]
        values = [self._critique_signal(report) for report in selected]
        handles = tuple(
            self._handle(
                ("editorialCritiqueReport", "candidateReports", index),
                "editorialCritique",
                str(report.get("candidateId") or f"critique-{index}"),
            )
            for index, report in enumerate(selected)
        )
        return ContextSelection(
            "critiqueSignals",
            values,
            handles,
            available=bool(reports),
            total_count=len(reports),
            selected_count=len(selected),
            trimmed_count=max(0, len(reports) - len(selected)),
        )

    def rejected_moves(self, limit: int = 12) -> ContextSelection:
        validation = self._mapping(self._index.step_payload("validation"))
        critique = self._mapping(validation.get("editorialCritiqueReport"))
        candidates = self._records(critique.get("candidateReports"))
        records: list[tuple[dict[str, Any], ArtifactHandle]] = []
        for report_index, report in enumerate(candidates):
            for finding_index, finding in enumerate(self._records(report.get("findings"))):
                severity = str(finding.get("severity") or "").lower()
                if severity not in {"warning", "critical"}:
                    continue
                value = self._select(
                    finding,
                    ("validatorId", "severity", "message", "repairGuidance", "status", "source"),
                )
                value["candidateId"] = report.get("candidateId")
                handle = self._handle(
                    ("editorialCritiqueReport", "candidateReports", report_index, "findings", finding_index),
                    "rejectedMove",
                    self._finding_artifact_id(finding, report, finding_index),
                )
                records.append((value, handle))
        selected = records[: max(0, limit)]
        return ContextSelection(
            "rejectedMoves",
            [value for value, _ in selected],
            tuple(handle for _, handle in selected),
            available=bool(records),
            total_count=len(records),
            selected_count=len(selected),
            trimmed_count=max(0, len(records) - len(selected)),
        )

    def route(self) -> ContextSelection:
        validation = self._mapping(self._index.step_payload("validation"))
        tournament = self._mapping(validation.get("alternativeAngleTournament"))
        route = self._mapping(tournament.get("route"))
        if not route:
            return ContextSelection("alternativeRoute", None, available=False)
        value = self._select(
            route,
            (
                "id",
                "title",
                "angle",
                "openingMove",
                "whyDifferent",
                "critiqueInputs",
                "claimsToUse",
                "claimsToAvoid",
                "rulesToStress",
                "risks",
            ),
        )
        handle = self._handle(("alternativeAngleTournament", "route"), "alternativeAngleRoute", str(route.get("id") or "route"))
        return ContextSelection("alternativeRoute", value, (handle,), total_count=1, selected_count=1)

    def _handle(self, path: tuple[str | int, ...], artifact_type: str, artifact_id: str) -> ArtifactHandle:
        return ArtifactHandle.create(
            run_id=self._index.run_id,
            step_key="validation",
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            path=path,
        )

    def _finding_artifact_id(
        self,
        finding: Mapping[str, Any],
        report: Mapping[str, Any],
        finding_index: int,
    ) -> str:
        if finding.get("id"):
            return str(finding["id"])
        candidate_id = finding.get("candidateId") or report.get("candidateId")
        validator_id = finding.get("validatorId")
        if candidate_id and validator_id:
            return f"{candidate_id}:{validator_id}"
        return str(validator_id or candidate_id or f"finding-{finding_index}")

    def _select(self, value: Mapping[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
        return {key: self._bounded(value.get(key)) for key in keys if value.get(key) not in (None, [], {})}

    def _critique_signal(self, report: Mapping[str, Any]) -> dict[str, Any]:
        compact = self._select(
            report,
            (
                "candidateId",
                "status",
                "summary",
                "editorialRisk",
                "weakestMove",
                "recommendedEditorialMove",
            ),
        )
        compact["tensions"] = [self._bounded_to(item, 240) for item in self._values(report.get("tensions"))[:3]]
        compact["findings"] = [
            self._select_bounded(finding, ("validatorId", "severity", "message"), 300)
            for finding in self._records(report.get("findings"))[:3]
        ]
        return {key: value for key, value in compact.items() if value not in (None, [], {})}

    def _select_bounded(self, value: Mapping[str, Any], keys: tuple[str, ...], text_limit: int) -> dict[str, Any]:
        return {
            key: self._bounded_to(value.get(key), text_limit)
            for key in keys
            if value.get(key) not in (None, [], {})
        }

    def _bounded_to(self, value: Any, text_limit: int) -> Any:
        if isinstance(value, str):
            return value[:text_limit]
        if isinstance(value, Mapping):
            return {str(key): self._bounded_to(child, text_limit) for key, child in list(value.items())[:8]}
        if isinstance(value, list):
            return [self._bounded_to(child, text_limit) for child in value[:4]]
        return value

    def _values(self, value: Any) -> list[Any]:
        return list(value) if isinstance(value, list) else []

    def _bounded(self, value: Any) -> Any:
        if isinstance(value, str):
            return value[:600]
        if isinstance(value, Mapping):
            return {str(key): self._bounded(child) for key, child in list(value.items())[:12]}
        if isinstance(value, list):
            return [self._bounded(child) for child in value[:8]]
        return value

    def _mapping(self, value: Any) -> Mapping[str, Any]:
        return value if isinstance(value, Mapping) else {}

    def _records(self, value: Any) -> list[dict[str, Any]]:
        return [dict(item) for item in value if isinstance(item, Mapping)] if isinstance(value, list) else []


__all__ = ("AlternativeAngleContextReader",)
