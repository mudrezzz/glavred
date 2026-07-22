"""Owner: upstream.application

Used by: authenticated project-scoped source-signal review API.
Does not own: authentication, provider scoring, evidence mutation, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from backend.app.upstream.domain.signal_review import (
    SourceSignalReviewCommand,
    SourceSignalReviewError,
    SourceSignalReviewResult,
)


class SourceSignalReviewLifecyclePolicy:
    _TRANSITIONS = {
        "candidate": {"approve": "approved", "reject": "rejected", "archive": "archived", "correct": "corrected"},
        "new": {"approve": "approved", "reject": "rejected", "archive": "archived", "correct": "corrected"},
        "corrected": {"approve": "approved", "reject": "rejected", "archive": "archived", "correct": "corrected"},
        "approved": {"reopen": "candidate"},
        "rejected": {"reopen": "candidate"},
        "archived": {"restore": "candidate"},
    }
    _REASON_REQUIRED = {"reject", "archive", "correct"}
    _EDITABLE_FIELDS = {"title", "summary", "authorCorrection"}

    def apply(self, signal: dict, command: SourceSignalReviewCommand) -> SourceSignalReviewResult:
        current_revision = int(signal.get("reviewRevision") or 0)
        if current_revision != command.expected_revision:
            raise SourceSignalReviewError("signal-review-revision-conflict")
        current_status = str(signal.get("reviewStatus") or "candidate")
        target = self._TRANSITIONS.get(current_status, {}).get(command.action)
        if not target:
            raise SourceSignalReviewError("signal-review-transition-not-allowed")
        reason = command.reason.strip()
        if command.action in self._REASON_REQUIRED and not reason:
            raise SourceSignalReviewError("signal-review-reason-required")
        patch = {
            key: " ".join(str(value).split())
            for key, value in command.editorial_patch.items()
            if key in self._EDITABLE_FIELDS
        }
        if command.action != "correct" and patch:
            raise SourceSignalReviewError("signal-review-patch-only-allowed-for-correction")
        changed_fields = [key for key, value in patch.items() if value != signal.get(key)]
        next_revision = current_revision + 1
        event = {
            "id": f"signal-review-{uuid4()}",
            "actorId": command.actor_id,
            "occurredAt": datetime.now(UTC).isoformat(),
            "action": command.action,
            "fromStatus": current_status,
            "toStatus": target,
            "reason": reason,
            "changedFields": changed_fields,
            "reviewRevision": next_revision,
        }
        updated = {
            **signal,
            **patch,
            "reviewStatus": target,
            "reviewRevision": next_revision,
            "reviewHistory": [*list(signal.get("reviewHistory") or []), event],
        }
        utility_stale = command.action == "correct" and bool(changed_fields)
        if utility_stale and isinstance(updated.get("utilityReport"), dict):
            updated["utilityReport"] = {
                **updated["utilityReport"],
                "status": "stale",
                "staleReason": "editorial-correction",
            }
        return SourceSignalReviewResult(signal=updated, utility_stale=utility_stale)


__all__ = ("SourceSignalReviewLifecyclePolicy",)
