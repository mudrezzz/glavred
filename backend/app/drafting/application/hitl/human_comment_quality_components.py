"""Owner: drafting.application.hitl

Used by: Human-comment quality check service.
Does not own: Provider execution, prompt construction, API response mapping, or persistence.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

import re
from typing import Any

from backend.app.domain.draft_human_revision import HumanCommentRevisionQualityCheck

INTERNAL_JARGON_TERMS = ["SourceLedger", "publicEvidence", "validators", "PostContract", "RuleRegistry"]
SOURCE_MARKER_CANDIDATES = [
    "B2BNotes",
    "WebProNews",
    "RAND",
    "RAND Corporation",
    "NSSG",
    "NSSG Insights",
    "Gartner",
    "McKinsey",
    "Forrester",
]


class HumanCommentQualityPayloadParser:
    def parse(self, payload: dict[str, Any], attempts: list[dict[str, Any]]) -> HumanCommentRevisionQualityCheck:
        status = self._status(payload.get("status"))
        comment_status = self._status(payload.get("commentComplianceStatus"))
        source_status = self._status(payload.get("sourceIntegrityStatus"))
        prose_status = self._status(payload.get("publicProseStatus"))
        worst_status = self.worst_status([status, comment_status, source_status, prose_status])
        return HumanCommentRevisionQualityCheck(
            status=worst_status,
            comment_compliance_status=comment_status,
            source_integrity_status=source_status,
            public_prose_status=prose_status,
            internal_jargon_leaks=self._strings(payload.get("internalJargonLeaks")),
            regression_warnings=self._strings(payload.get("regressionWarnings")),
            matched_comment_intents=self._strings(payload.get("matchedCommentIntents")),
            missed_comment_intents=self._strings(payload.get("missedCommentIntents")),
            summary=str(payload.get("summary") or "").strip(),
            attempts=attempts,
        )

    def worst_status(self, values: list[str]) -> str:
        rank = {"passed": 0, "notRun": 0, "warning": 1, "critical": 2}
        return max(values, key=lambda item: rank.get(item, 1))

    def _status(self, value: Any) -> str:
        normalized = str(value or "").strip()
        return normalized if normalized in {"passed", "warning", "critical", "notRun"} else "warning"

    def _strings(self, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item).strip() for item in value if str(item).strip()]


class HumanCommentQualityOverlayPolicy:
    def __init__(self, parser: HumanCommentQualityPayloadParser | None = None) -> None:
        self._parser = parser or HumanCommentQualityPayloadParser()

    def apply(
        self,
        check: HumanCommentRevisionQualityCheck,
        *,
        base_body: str,
        revised_body: str,
    ) -> HumanCommentRevisionQualityCheck:
        leaks = list(dict.fromkeys([*check.internal_jargon_leaks, *[term for term in INTERNAL_JARGON_TERMS if term in revised_body]]))
        lost_markers = [
            marker
            for marker in SOURCE_MARKER_CANDIDATES
            if self._contains_marker(base_body, marker) and not self._contains_marker(revised_body, marker)
        ]
        regression_warnings = list(check.regression_warnings)
        if lost_markers:
            regression_warnings.append(f"Lost visible source markers: {', '.join(lost_markers)}")
        source_status = self._worse(check.source_integrity_status, "warning" if lost_markers else "passed")
        prose_status = self._worse(check.public_prose_status, "warning" if leaks else "passed")
        status = self._parser.worst_status([check.status, check.comment_compliance_status, source_status, prose_status])
        return HumanCommentRevisionQualityCheck(
            status=status,
            comment_compliance_status=check.comment_compliance_status,
            source_integrity_status=source_status,
            public_prose_status=prose_status,
            internal_jargon_leaks=leaks,
            regression_warnings=regression_warnings,
            matched_comment_intents=check.matched_comment_intents,
            missed_comment_intents=check.missed_comment_intents,
            summary=check.summary,
            attempts=check.attempts,
        )

    def _worse(self, left: str, right: str) -> str:
        return self._parser.worst_status([left, right])

    def _contains_marker(self, body: str, marker: str) -> bool:
        return re.search(rf"(?<!\w){re.escape(marker)}(?!\w)", body, flags=re.IGNORECASE) is not None
