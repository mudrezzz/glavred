"""Owner: drafting.domain

Used by: provider dossier policies and payload budget policies.
Does not own: payload compaction, prompt construction, provider calls, or trace persistence.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SemanticInputContract:
    must_have: tuple[str, ...] = ()
    should_have: tuple[str, ...] = ()
    diagnostic_only: tuple[str, ...] = ()
    never_send_to_provider: tuple[str, ...] = ()

    def to_payload(self) -> dict[str, list[str]]:
        return {
            "mustHave": list(self.must_have),
            "shouldHave": list(self.should_have),
            "diagnosticOnly": list(self.diagnostic_only),
            "neverSendToProvider": list(self.never_send_to_provider),
        }


__all__ = ("SemanticInputContract",)
