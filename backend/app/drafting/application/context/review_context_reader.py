"""Owner: drafting.application.context

Used by: review, ranking, revision, and final-quality dossier factories.
Does not own: provider calls, prompt construction, budgets, or lifecycle decisions.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from backend.app.drafting.application.context.draft_run_artifact_index import DraftRunArtifactIndex
from backend.app.drafting.domain.provider_dossier import ArtifactHandle, ContextSelection


class ReviewContextReader:
    def __init__(self, index: DraftRunArtifactIndex) -> None:
        self._index = index

    def validation_issues(self, candidate_id: str | None = None, limit: int = 20) -> ContextSelection:
        report, base_path, report_available = self._validation_report()
        rows: list[tuple[dict[str, Any], ArtifactHandle]] = []
        report_sets = (
            ("deterministic", self._records(report.get("candidateReports")), ("candidateReports",)),
            ("llmValidation", self._records(self._mapping(report.get("llmValidationReport")).get("candidateReports")), ("llmValidationReport", "candidateReports")),
            ("editorialCritique", self._records(self._mapping(report.get("editorialCritiqueReport")).get("candidateReports")), ("editorialCritiqueReport", "candidateReports")),
        )
        seen: set[tuple[str, str, str, str]] = set()
        for source, reports, report_path in report_sets:
            for report_index, candidate_report in enumerate(reports):
                report_candidate_id = str(candidate_report.get("candidateId") or "")
                if candidate_id and report_candidate_id != str(candidate_id):
                    continue
                for finding_index, finding in enumerate(self._records(candidate_report.get("findings"))):
                    identity = (
                        report_candidate_id,
                        source,
                        str(finding.get("validatorId") or finding.get("id") or "unknown"),
                        str(finding.get("message") or ""),
                    )
                    if identity in seen:
                        continue
                    seen.add(identity)
                    compact = self._select(
                        finding,
                        ("id", "validatorId", "severity", "message", "repairGuidance", "evidenceExcerpt", "ruleIds", "claimIds", "metadata"),
                    )
                    compact.update({"candidateId": report_candidate_id or None, "source": source})
                    path = (*base_path, *report_path, report_index, "findings", finding_index)
                    handle = self._handle("validation", path, "validationIssue", self._issue_id(identity, finding, finding_index))
                    rows.append((compact, handle))
        rows.sort(key=lambda item: (0 if item[0].get("severity") == "critical" else 1, str(item[0].get("validatorId") or "")))
        selected = rows[: max(0, limit)]
        return ContextSelection(
            "validationIssues",
            [item for item, _ in selected],
            tuple(handle for _, handle in selected),
            available=report_available,
            total_count=len(rows),
            selected_count=len(selected),
            trimmed_count=max(0, len(rows) - len(selected)),
        )

    def revision_instruction(self) -> ContextSelection:
        checkpoint = self._checkpoint()
        value = self._mapping(checkpoint.get("revisionInstruction"))
        if value:
            return self._checkpoint_selection("revisionInstruction", value)
        ranking = self._ranking_revision()
        value = self._mapping(ranking.get("revisionInstruction"))
        return self._validation_selection("revisionInstruction", value, ("rankingRevision", "revisionInstruction"))

    def final_quality_contract(self) -> ContextSelection:
        checkpoint = self._checkpoint()
        value = self._mapping(checkpoint.get("finalQualityContract"))
        if value:
            return self._checkpoint_selection("finalQualityContract", value)
        value = self._mapping(self._final_quality_gate().get("finalQualityContract"))
        return self._validation_selection("finalQualityContract", value, ("rankingRevision", "finalQualityGate", "finalQualityContract"))

    def deterministic_gate(self) -> ContextSelection:
        checkpoint = self._checkpoint()
        value = self._mapping(checkpoint.get("deterministicGate"))
        if value:
            return self._checkpoint_selection("deterministicGate", value)
        value = self._mapping(self._final_quality_gate().get("deterministicGate"))
        return self._validation_selection("deterministicGate", value, ("rankingRevision", "finalQualityGate", "deterministicGate"))

    def repair_history(self) -> ContextSelection:
        checkpoint = self._checkpoint()
        value = self._mapping(checkpoint.get("repairHistory"))
        if value:
            return self._checkpoint_selection("repairHistory", value)
        validation = self._mapping(self._index.step_payload("validation"))
        loop = self._mapping(self._mapping(validation.get("rankingRevision")).get("revisionLoop"))
        if not loop:
            return self._missing("repairHistory")
        compact = self._select(loop, ("status", "stopReason", "cycles"))
        handle = self._handle("validation", ("rankingRevision", "revisionLoop"), "revisionLoop", "artifact")
        return ContextSelection("repairHistory", compact, (handle,), total_count=1, selected_count=1)

    def final_quality_lifecycle(self, limit: int = 20) -> ContextSelection:
        validation = self._mapping(self._index.step_payload("validation"))
        quality = self._mapping(self._mapping(validation.get("rankingRevision")).get("qualityFidelity"))
        lifecycle = self._mapping(quality.get("issueLifecycle"))
        items = self._records(lifecycle.get("items"))[: max(0, limit)]
        if not quality:
            return self._missing("finalQualityIssues")
        value = {
            "status": quality.get("editorialStatus"),
            "overallVerdict": quality.get("overallVerdict"),
            "items": [self._select(item, ("id", "candidateId", "validatorId", "severity", "status", "scope", "message", "statusReason")) for item in items],
        }
        handle = self._handle("validation", ("rankingRevision", "qualityFidelity", "issueLifecycle"), "finalQualityIssues", "artifact")
        return ContextSelection("finalQualityIssues", value, (handle,), total_count=len(items), selected_count=len(items))

    def _validation_report(self) -> tuple[Mapping[str, Any], tuple[str | int, ...], bool]:
        checkpoint = self._checkpoint()
        if "validationReport" in checkpoint:
            return self._mapping(checkpoint.get("validationReport")), ("reviewContext", "validationReport"), True
        validation = self._mapping(self._index.step_payload("validation"))
        return validation, (), bool(validation)

    def _checkpoint(self) -> Mapping[str, Any]:
        return self._mapping(self._mapping(self._index.step_payload("validation")).get("reviewContext"))

    def _checkpoint_selection(self, key: str, value: Mapping[str, Any]) -> ContextSelection:
        if not value:
            return self._missing(key)
        artifact_id = str(value.get("id") or value.get("candidateId") or "artifact")
        handle = self._handle("validation", ("reviewContext", key), key, artifact_id)
        return ContextSelection(key, dict(value), (handle,), total_count=1, selected_count=1)

    def _validation_selection(
        self,
        key: str,
        value: Mapping[str, Any],
        path: tuple[str | int, ...],
    ) -> ContextSelection:
        if not value:
            return self._missing(key)
        artifact_id = str(value.get("id") or value.get("candidateId") or "artifact")
        handle = self._handle("validation", path, key, artifact_id)
        return ContextSelection(key, dict(value), (handle,), total_count=1, selected_count=1)

    def _ranking_revision(self) -> Mapping[str, Any]:
        validation = self._mapping(self._index.step_payload("validation"))
        return self._mapping(validation.get("rankingRevision"))

    def _final_quality_gate(self) -> Mapping[str, Any]:
        return self._mapping(self._ranking_revision().get("finalQualityGate"))

    def _issue_id(self, identity: tuple[str, str, str, str], finding: Mapping[str, Any], index: int) -> str:
        if finding.get("id"):
            return str(finding["id"])
        if identity[0] and identity[2]:
            return f"{identity[0]}:{identity[2]}"
        return identity[2] or identity[0] or f"finding-{index}"

    def _handle(self, step_key: str, path: tuple[str | int, ...], artifact_type: str, artifact_id: str) -> ArtifactHandle:
        return ArtifactHandle.create(run_id=self._index.run_id, step_key=step_key, artifact_type=artifact_type, artifact_id=artifact_id, path=path)

    def _missing(self, key: str) -> ContextSelection:
        return ContextSelection(key, None, available=False)

    def _select(self, value: Mapping[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
        return {key: value.get(key) for key in keys if value.get(key) not in (None, [], {})}

    def _mapping(self, value: Any) -> Mapping[str, Any]:
        return value if isinstance(value, Mapping) else {}

    def _records(self, value: Any) -> list[dict[str, Any]]:
        return [dict(item) for item in value if isinstance(item, Mapping)] if isinstance(value, list) else []


__all__ = ("ReviewContextReader",)
