"""Owner: upstream.domain

Used by: source signal review lifecycle and project-scoped review API.
Does not own: utility scoring, evidence mutation, authentication, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SourceSignalReviewCommand:
    action: str
    actor_id: str
    reason: str
    expected_revision: int
    editorial_patch: dict[str, str]


@dataclass(frozen=True)
class SourceSignalReviewResult:
    signal: dict[str, Any]
    utility_stale: bool


class SourceSignalReviewError(ValueError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


__all__ = ("SourceSignalReviewCommand", "SourceSignalReviewError", "SourceSignalReviewResult")
