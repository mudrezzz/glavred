from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class DraftValidatorStatus(StrEnum):
    PASSED = "passed"
    WARNING = "warning"
    CRITICAL = "critical"
    NOT_RUN = "not-run"


@dataclass(frozen=True)
class DraftValidatorFinding:
    validator_id: str
    severity: DraftValidatorStatus
    candidate_id: str
    message: str
    evidence_excerpt: str
    repair_guidance: str
    rule_ids: list[str] = field(default_factory=list)
    claim_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "validatorId": self.validator_id,
            "severity": self.severity.value,
            "candidateId": self.candidate_id,
            "ruleIds": self.rule_ids,
            "claimIds": self.claim_ids,
            "message": self.message,
            "evidenceExcerpt": self.evidence_excerpt,
            "repairGuidance": self.repair_guidance,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class DraftCandidateValidationReport:
    candidate_id: str
    selected: bool
    status: DraftValidatorStatus
    findings: list[DraftValidatorFinding] = field(default_factory=list)

    @property
    def critical_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == DraftValidatorStatus.CRITICAL)

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == DraftValidatorStatus.WARNING)

    def to_payload(self) -> dict[str, Any]:
        return {
            "candidateId": self.candidate_id,
            "selected": self.selected,
            "status": self.status.value,
            "criticalCount": self.critical_count,
            "warningCount": self.warning_count,
            "findings": [finding.to_payload() for finding in self.findings],
        }


@dataclass(frozen=True)
class DraftValidationReport:
    selected_candidate_id: str | None
    candidate_reports: list[DraftCandidateValidationReport]
    status: DraftValidatorStatus = DraftValidatorStatus.PASSED
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def critical_count(self) -> int:
        return sum(report.critical_count for report in self.candidate_reports)

    @property
    def warning_count(self) -> int:
        return sum(report.warning_count for report in self.candidate_reports)

    def to_payload(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "selectedCandidateId": self.selected_candidate_id,
            "summary": {
                "candidateCount": len(self.candidate_reports),
                "criticalCount": self.critical_count,
                "warningCount": self.warning_count,
                "selectedStatus": _selected_status(self.candidate_reports),
            },
            "candidateReports": [report.to_payload() for report in self.candidate_reports],
            "metadata": {"version": "draft-validation-v1", "reportOnly": True, **self.metadata},
        }


def validation_status_for(findings: list[DraftValidatorFinding]) -> DraftValidatorStatus:
    if any(finding.severity == DraftValidatorStatus.CRITICAL for finding in findings):
        return DraftValidatorStatus.CRITICAL
    if any(finding.severity == DraftValidatorStatus.WARNING for finding in findings):
        return DraftValidatorStatus.WARNING
    return DraftValidatorStatus.PASSED


def report_status_for(reports: list[DraftCandidateValidationReport]) -> DraftValidatorStatus:
    if any(report.status == DraftValidatorStatus.CRITICAL for report in reports):
        return DraftValidatorStatus.CRITICAL
    if any(report.status == DraftValidatorStatus.WARNING for report in reports):
        return DraftValidatorStatus.WARNING
    return DraftValidatorStatus.PASSED if reports else DraftValidatorStatus.NOT_RUN


def _selected_status(reports: list[DraftCandidateValidationReport]) -> str | None:
    selected = next((report for report in reports if report.selected), None)
    return selected.status.value if selected else None
