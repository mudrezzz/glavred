"""Owner: drafting.application.hitl

Used by: Human-comment HITL services and prompt builders.
Does not own: Provider execution, API routing, persistence, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any, Protocol

from backend.app.domain.draft_run import DraftRun


class HumanCommentVersionCompactor:
    def compact(self, version: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": version.get("id"),
            "versionNumber": version.get("versionNumber"),
            "title": version.get("title"),
            "body": version.get("body"),
        }


class DraftRunLookup(Protocol):
    def get(self, run_id: str) -> DraftRun | None: ...


class HumanCommentTraceContextBuilder:
    def __init__(self, draft_run_repository: DraftRunLookup) -> None:
        self._draft_run_repository = draft_run_repository

    def build(self, draft_run_id: str | None) -> dict[str, Any]:
        if not draft_run_id:
            return {"draftRunId": None, "traceStatus": "unavailable"}
        run = self._draft_run_repository.get(draft_run_id)
        if not run:
            return {"draftRunId": draft_run_id, "traceStatus": "unavailable"}
        validation = self._step_artifact(run, "validation")
        ranking_revision = self._record(validation.get("rankingRevision"))
        return {
            "draftRunId": draft_run_id,
            "traceStatus": "available",
            "finalQualityGate": ranking_revision.get("finalQualityGate"),
            "revisionLoop": ranking_revision.get("revisionLoop"),
            "alternativeAngleTournament": validation.get("alternativeAngleTournament"),
            "validationSummary": self._validation_summary(validation),
        }

    def _step_artifact(self, run: DraftRun, key: str) -> dict[str, Any]:
        for step in run.steps:
            if step.key.value == key and isinstance(step.artifact_payload, dict):
                return step.artifact_payload
        return {}

    def _validation_summary(self, validation: dict[str, Any]) -> dict[str, Any]:
        candidate_reports = validation.get("candidateReports")
        llm_report = self._record(validation.get("llmValidationReport"))
        return {
            "deterministicCandidateCount": len(candidate_reports) if isinstance(candidate_reports, list) else 0,
            "llmCandidateCount": len(llm_report.get("candidateReports")) if isinstance(llm_report.get("candidateReports"), list) else 0,
            "status": validation.get("status") or llm_report.get("status"),
        }

    def _record(self, value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}
