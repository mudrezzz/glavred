from dataclasses import dataclass, field
from typing import Any

from backend.app.domain.draft_validation import DraftValidatorFinding, DraftValidatorStatus, validation_status_for


@dataclass(frozen=True)
class LlmValidatorAttempt:
    label: str
    model: str | None
    status: str
    candidate_id: str
    ai_run_id: str | None = None
    backup: bool = False
    validation: str | None = None

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "label": self.label,
            "model": self.model,
            "status": self.status,
            "candidateId": self.candidate_id,
            "aiRunId": self.ai_run_id,
            "backup": self.backup,
        }
        if self.validation:
            payload["validation"] = self.validation
        return payload


@dataclass(frozen=True)
class LlmCandidateValidationReport:
    candidate_id: str
    status: DraftValidatorStatus
    findings: list[DraftValidatorFinding] = field(default_factory=list)
    attempts: list[LlmValidatorAttempt] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        return {
            "candidateId": self.candidate_id,
            "status": self.status.value,
            "criticalCount": sum(1 for finding in self.findings if finding.severity == DraftValidatorStatus.CRITICAL),
            "warningCount": sum(1 for finding in self.findings if finding.severity == DraftValidatorStatus.WARNING),
            "findings": [finding.to_payload() for finding in self.findings],
            "attempts": [attempt.to_payload() for attempt in self.attempts],
        }


@dataclass(frozen=True)
class LlmDraftValidationReport:
    status: DraftValidatorStatus
    candidate_reports: list[LlmCandidateValidationReport] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "summary": {
                "candidateCount": len(self.candidate_reports),
                "criticalCount": sum(report.to_payload()["criticalCount"] for report in self.candidate_reports),
                "warningCount": sum(report.to_payload()["warningCount"] for report in self.candidate_reports),
            },
            "candidateReports": [report.to_payload() for report in self.candidate_reports],
            "metadata": {"version": "llm-draft-validation-v1", "reportOnly": True, **self.metadata},
        }


def llm_report_status(reports: list[LlmCandidateValidationReport]) -> DraftValidatorStatus:
    if not reports:
        return DraftValidatorStatus.NOT_RUN
    if any(report.status == DraftValidatorStatus.NOT_RUN for report in reports):
        return DraftValidatorStatus.WARNING
    return validation_status_for([finding for report in reports for finding in report.findings])
