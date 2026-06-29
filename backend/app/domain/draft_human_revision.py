from dataclasses import dataclass, field
from typing import Any, Literal

HumanCommentRevisionQualityStatus = Literal["passed", "warning", "critical", "notRun"]
HumanCommentRevisionCheckStatus = Literal["passed", "warning", "critical", "notRun"]


@dataclass(frozen=True)
class HumanCommentRevisionQualityCheck:
    status: HumanCommentRevisionQualityStatus
    comment_compliance_status: HumanCommentRevisionCheckStatus = "notRun"
    source_integrity_status: HumanCommentRevisionCheckStatus = "notRun"
    public_prose_status: HumanCommentRevisionCheckStatus = "notRun"
    internal_jargon_leaks: list[str] = field(default_factory=list)
    regression_warnings: list[str] = field(default_factory=list)
    matched_comment_intents: list[str] = field(default_factory=list)
    missed_comment_intents: list[str] = field(default_factory=list)
    summary: str = ""
    attempts: list[dict[str, Any]] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "commentComplianceStatus": self.comment_compliance_status,
            "sourceIntegrityStatus": self.source_integrity_status,
            "publicProseStatus": self.public_prose_status,
            "internalJargonLeaks": self.internal_jargon_leaks,
            "regressionWarnings": self.regression_warnings,
            "matchedCommentIntents": self.matched_comment_intents,
            "missedCommentIntents": self.missed_comment_intents,
            "summary": self.summary,
            "attempts": self.attempts,
        }


def human_comment_revision_quality_not_run(*, reason: str, attempts: list[dict[str, Any]] | None = None) -> HumanCommentRevisionQualityCheck:
    return HumanCommentRevisionQualityCheck(
        status="notRun",
        comment_compliance_status="notRun",
        source_integrity_status="notRun",
        public_prose_status="notRun",
        summary=reason,
        attempts=attempts or [],
    )
