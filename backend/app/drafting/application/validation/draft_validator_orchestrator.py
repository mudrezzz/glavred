"""Owner: drafting.application.validation

Used by: DraftRun validation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.validation.draft_validation_linter import DeterministicDraftLinter
from backend.app.domain.draft_validation import (
    DraftCandidateValidationReport,
    DraftValidationReport,
    DraftValidatorStatus,
    report_status_for,
    validation_status_for,
)


class DraftValidatorOrchestrator:
    def __init__(self, linter: DeterministicDraftLinter | None = None) -> None:
        self._linter = linter or DeterministicDraftLinter()

    def validate(
        self,
        *,
        draft_artifact: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
    ) -> DraftValidationReport:
        candidates = _list_of_dicts(draft_artifact.get("candidates"))
        selection = _dict(draft_artifact.get("selection"))
        selected_candidate_id = _optional_string(selection.get("selectedCandidateId"))
        scorecard = {
            str(row.get("candidateId")): row
            for row in _list_of_dicts(selection.get("scorecard"))
            if row.get("candidateId")
        }
        reports = [
            self._candidate_report(
                candidate=candidate,
                selected_candidate_id=selected_candidate_id,
                context_artifact=context_artifact,
                rule_pack=rule_pack,
                material_plan=material_plan,
                score_row=scorecard.get(str(candidate.get("id"))),
            )
            for candidate in candidates
        ]
        return DraftValidationReport(
            selected_candidate_id=selected_candidate_id,
            candidate_reports=reports,
            status=report_status_for(reports),
            metadata={"validator": "deterministic-v1"},
        )

    def not_run(self, *, reason: str) -> DraftValidationReport:
        return DraftValidationReport(
            selected_candidate_id=None,
            candidate_reports=[],
            status=DraftValidatorStatus.NOT_RUN,
            metadata={"validator": "deterministic-v1", "reason": reason},
        )

    def _candidate_report(
        self,
        *,
        candidate: dict[str, Any],
        selected_candidate_id: str | None,
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        score_row: dict[str, Any] | None,
    ) -> DraftCandidateValidationReport:
        candidate_id = str(candidate.get("id") or "unknown-candidate")
        findings = self._linter.lint(
            candidate=candidate,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
            score_row=score_row,
        )
        return DraftCandidateValidationReport(
            candidate_id=candidate_id,
            selected=selected_candidate_id == candidate_id,
            status=validation_status_for(findings),
            findings=findings,
        )


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _optional_string(value: Any) -> str | None:
    return str(value) if value else None
