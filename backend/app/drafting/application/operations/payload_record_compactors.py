"""Owner: drafting.application.operations

Used by: Payload budget compactors for compact record projections.
Does not own: Operation-level payload policy or provider messages.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from typing import Any

from backend.app.drafting.application.operations.payload_compactor_common import _drop_empty, _pick, _record


class EvidenceRecordCompactor:
    @staticmethod
    def compact_claim(claim: dict[str, Any]) -> dict[str, Any]:
        return _drop_empty(
            {
                **_pick(claim, ("id", "type", "statement", "allowedUse", "confidence", "risk", "sourceId", "publicEvidenceItemId", "sourceTitle", "sourceUrl")),
                "provenance": _pick(_record(claim.get("provenance")), ("publicEvidenceItemId", "sourceTitle", "sourceUrl", "sourceLabel", "snippet")),
            }
        )

    @staticmethod
    def compact_evidence_item(item: dict[str, Any]) -> dict[str, Any]:
        return _pick(item, ("id", "sourceTitle", "sourceUrl", "snippet", "summary", "allowedUse", "confidence", "attemptId"))


class CandidatePayloadCompactor:
    @staticmethod
    def compact(candidate: dict[str, Any]) -> dict[str, Any]:
        return _pick(candidate, ("id", "baseCandidateId", "title", "body", "rationale", "usedEvidence", "ruleCoverage", "risks", "weaknesses", "source", "score", "fallbackUsed"))


class SummaryRecordCompactor:
    @staticmethod
    def compact(payload: dict[str, Any]) -> dict[str, Any]:
        return _pick(payload, ("id", "status", "summary", "reason", "decision", "winnerId", "accepted", "rejected", "findings", "warnings", "repairGoals", "metadata"))
