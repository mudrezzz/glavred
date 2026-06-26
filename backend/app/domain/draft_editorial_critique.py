from dataclasses import dataclass, field
from typing import Any

from backend.app.domain.draft_validation import DraftValidatorFinding, DraftValidatorStatus, validation_status_for


@dataclass(frozen=True)
class EditorialCritiqueObservation:
    critic_id: str
    candidate_id: str
    message: str
    evidence_excerpt: str = ""
    editorial_dimension: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "criticId": self.critic_id,
            "candidateId": self.candidate_id,
            "message": self.message,
            "evidenceExcerpt": self.evidence_excerpt,
            "editorialDimension": self.editorial_dimension,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class EditorialCriticAttempt:
    label: str
    model: str | None
    status: str
    candidate_id: str
    ai_run_id: str | None = None
    backup: bool = False
    validation: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

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
        payload.update(self.metadata)
        return payload


@dataclass(frozen=True)
class EditorialCandidateCritique:
    candidate_id: str
    status: DraftValidatorStatus
    editorial_risk: str = "unknown"
    overall_judgment: str = ""
    strongest_move: str = ""
    weakest_move: str = ""
    recommended_editorial_move: str = ""
    findings: tuple[DraftValidatorFinding, ...] = ()
    observations: tuple[EditorialCritiqueObservation, ...] = ()
    attempts: tuple[EditorialCriticAttempt, ...] = ()

    def to_payload(self) -> dict[str, Any]:
        return {
            "candidateId": self.candidate_id,
            "status": self.status.value,
            "editorialRisk": self.editorial_risk,
            "overallJudgment": self.overall_judgment,
            "strongestMove": self.strongest_move,
            "weakestMove": self.weakest_move,
            "recommendedEditorialMove": self.recommended_editorial_move,
            "findingCount": len(self.findings),
            "observationCount": len(self.observations),
            "findings": [finding.to_payload() for finding in self.findings],
            "observations": [observation.to_payload() for observation in self.observations],
            "attempts": [attempt.to_payload() for attempt in self.attempts],
        }


@dataclass(frozen=True)
class EditorialCritiqueReport:
    status: DraftValidatorStatus
    candidate_reports: tuple[EditorialCandidateCritique, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        high_risk = sum(1 for report in self.candidate_reports if report.editorial_risk == "high")
        return {
            "status": self.status.value,
            "summary": {
                "candidateCount": len(self.candidate_reports),
                "findingCount": sum(len(report.findings) for report in self.candidate_reports),
                "observationCount": sum(len(report.observations) for report in self.candidate_reports),
                "highRiskCandidateCount": high_risk,
            },
            "candidateReports": [report.to_payload() for report in self.candidate_reports],
            "metadata": {"version": "editorial-critique-v1", "reportOnly": True, **self.metadata},
        }


def editorial_critique_status(reports: list[EditorialCandidateCritique]) -> DraftValidatorStatus:
    if not reports:
        return DraftValidatorStatus.NOT_RUN
    if all(report.status == DraftValidatorStatus.NOT_RUN for report in reports):
        return DraftValidatorStatus.NOT_RUN
    if any(report.status == DraftValidatorStatus.NOT_RUN for report in reports):
        return DraftValidatorStatus.WARNING
    return validation_status_for([finding for report in reports for finding in report.findings])
