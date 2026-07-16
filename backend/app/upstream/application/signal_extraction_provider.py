"""Owner: upstream.application

Used by: SignalExtractionService as its typed provider boundary.
Does not own: OpenRouter HTTP details, extraction policy, retries, budgets, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class SignalExtractionProviderResult:
    payload: dict[str, Any]
    usage: dict[str, Any] | None
    request_id: str | None
    model: str | None


class SignalExtractionProvider(Protocol):
    def complete(
        self,
        *,
        messages: list[dict[str, str]],
        model: str,
        max_output_tokens: int,
    ) -> SignalExtractionProviderResult: ...


__all__ = ("SignalExtractionProvider", "SignalExtractionProviderResult")
