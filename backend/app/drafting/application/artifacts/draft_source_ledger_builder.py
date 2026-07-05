"""Owner: drafting.application.artifacts

Used by: DraftRun artifact migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.artifacts.draft_source_ledger_sections import (
    author_position_claims,
    base_forbidden_inferences,
    brief_claims,
    candidate_claims,
    risks,
    signal_claims,
    topic_fabula_claims,
    topic_forbidden_inferences,
    warnings,
)
from backend.app.domain.draft_generation import DraftGenerationRequest
from backend.app.domain.draft_source_ledger import SourceLedger


class SourceLedgerBuilder:
    def build(
        self,
        context_summary: dict[str, Any],
        request: DraftGenerationRequest | None = None,
    ) -> SourceLedger:
        candidate = _as_dict(context_summary.get("candidate"))
        signal = _as_dict(context_summary.get("sourceSignal"))
        topic = _as_dict(context_summary.get("topic"))
        fabula = _as_dict(context_summary.get("fabula"))
        author_evidence = _as_dict(context_summary.get("authorPositionEvidence"))

        return SourceLedger(
            claims=[
                *brief_claims(_as_dict(context_summary.get("brief")), request),
                *candidate_claims(candidate),
                *signal_claims(signal),
                *topic_fabula_claims(topic, fabula),
                *author_position_claims(author_evidence),
            ],
            risks=risks(candidate, request),
            forbidden_inferences=[
                *base_forbidden_inferences(),
                *topic_forbidden_inferences(topic),
            ],
            warnings=warnings(context_summary, candidate, signal, author_evidence, request),
            metadata={
                "version": "source-ledger-v1",
                "briefOnly": bool(context_summary.get("compatibility", {}).get("briefOnly")),
            },
        )


class SourceLedgerBuilderComponent:
    """Owns migrated helper behavior; module-level aliases remain compatibility-only."""

    @staticmethod
    def _as_dict(value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

_as_dict = SourceLedgerBuilderComponent._as_dict


__all__ = (
    'SourceLedgerBuilder',
    'SourceLedgerBuilderComponent',
)
