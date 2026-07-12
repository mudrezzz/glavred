"""Owner: drafting.application.revision

Used by: pairwise ranking prompts, payload validation, fallback trace, and replay diagnostics.
Does not own: winner selection, provider transport, prompt budgets, or revision acceptance.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Any, Iterable


EDITORIAL_DIMENSIONS = (
    "ideaStrength",
    "tension",
    "readerValue",
    "authorStance",
    "sourceIntegration",
    "structure",
    "validatorHealth",
)


@dataclass(frozen=True)
class PairwiseComparisonIdentityTrace:
    expected_pairs: tuple[tuple[str, str], ...]
    actual_pair_count: int
    missing_pairs: tuple[tuple[str, str], ...]
    duplicate_pairs: tuple[dict[str, Any], ...]
    invalid_pairs: tuple[dict[str, Any], ...]
    dimension_coverage: dict[str, Any]

    @property
    def complete(self) -> bool:
        return not self.missing_pairs and not self.duplicate_pairs and not self.invalid_pairs and bool(self.dimension_coverage.get("complete"))

    def to_payload(self) -> dict[str, Any]:
        return {
            "expectedPairCount": len(self.expected_pairs),
            "actualPairCount": self.actual_pair_count,
            "expectedPairs": [_pair_payload(pair) for pair in self.expected_pairs],
            "missingPairs": [_pair_payload(pair) for pair in self.missing_pairs],
            "duplicatePairs": [dict(item) for item in self.duplicate_pairs],
            "invalidPairs": [dict(item) for item in self.invalid_pairs],
            "comparisonIdentityComplete": self.complete,
            "dimensionCoverage": dict(self.dimension_coverage),
        }


class PairwisePayloadValidationError(ValueError):
    def __init__(self, trace: PairwiseComparisonIdentityTrace) -> None:
        super().__init__("Pairwise ranking comparison identity contract failed")
        self.trace = trace

    def to_payload(self) -> dict[str, Any]:
        return {"code": "pairwise-comparison-identity-invalid", **self.trace.to_payload()}


class PairwiseComparisonIdentityPolicy:
    """Validates exact unordered pair coverage and editorial-dimension identity."""

    def expected_pairs(self, candidate_ids: Iterable[str]) -> tuple[tuple[str, str], ...]:
        identities = tuple(dict.fromkeys(str(item) for item in candidate_ids if str(item)))
        return tuple(combinations(identities, 2))

    def evaluate(self, payload: dict[str, Any], candidate_ids: Iterable[str]) -> PairwiseComparisonIdentityTrace:
        identities = tuple(dict.fromkeys(str(item) for item in candidate_ids if str(item)))
        known = set(identities)
        order = {candidate_id: index for index, candidate_id in enumerate(identities)}
        expected = self.expected_pairs(identities)
        expected_set = set(expected)
        seen: set[tuple[str, str]] = set()
        duplicates: list[dict[str, Any]] = []
        invalid: list[dict[str, Any]] = []
        comparisons = payload.get("comparisons")
        rows = comparisons if isinstance(comparisons, list) else []

        if not isinstance(comparisons, list):
            invalid.append({"index": None, "reason": "comparisons-not-list"})
        for index, raw in enumerate(rows):
            if not isinstance(raw, dict):
                invalid.append({"index": index, "reason": "comparison-not-object"})
                continue
            left = str(raw.get("leftCandidateId") or "")
            right = str(raw.get("rightCandidateId") or "")
            winner = str(raw.get("winnerCandidateId") or "")
            reason = self._pair_error(left, right, winner, known)
            if reason:
                invalid.append({"index": index, "leftCandidateId": left, "rightCandidateId": right, "winnerCandidateId": winner, "reason": reason})
                continue
            pair = (left, right) if order[left] < order[right] else (right, left)
            if pair not in expected_set:
                invalid.append({"index": index, **_pair_payload(pair), "reason": "unexpected-pair"})
            elif pair in seen:
                duplicates.append({"index": index, **_pair_payload(pair), "reason": "duplicate-unordered-pair"})
            else:
                seen.add(pair)

        return PairwiseComparisonIdentityTrace(
            expected_pairs=expected,
            actual_pair_count=len(rows),
            missing_pairs=tuple(pair for pair in expected if pair not in seen),
            duplicate_pairs=tuple(duplicates),
            invalid_pairs=tuple(invalid),
            dimension_coverage=self._dimension_coverage(payload, known),
        )

    def validate(self, payload: dict[str, Any], candidate_ids: Iterable[str]) -> PairwiseComparisonIdentityTrace:
        trace = self.evaluate(payload, candidate_ids)
        winner = str(payload.get("winnerCandidateId") or "")
        if winner not in {str(item) for item in candidate_ids if str(item)}:
            invalid = (*trace.invalid_pairs, {"index": None, "winnerCandidateId": winner, "reason": "unknown-global-winner"})
            trace = PairwiseComparisonIdentityTrace(
                trace.expected_pairs,
                trace.actual_pair_count,
                trace.missing_pairs,
                trace.duplicate_pairs,
                invalid,
                trace.dimension_coverage,
            )
        if not trace.complete:
            raise PairwisePayloadValidationError(trace)
        return trace

    def _pair_error(self, left: str, right: str, winner: str, known: set[str]) -> str | None:
        if not left or not right or not winner:
            return "blank-candidate-identity"
        if left not in known or right not in known:
            return "unknown-pair-candidate"
        if left == right:
            return "self-pair"
        if winner not in (left, right):
            return "winner-outside-pair"
        return None

    def _dimension_coverage(self, payload: dict[str, Any], known: set[str]) -> dict[str, Any]:
        rows = payload.get("editorialDimensionScores")
        scores = rows if isinstance(rows, list) else []
        actual: list[str] = []
        invalid: list[dict[str, Any]] = []
        duplicates: list[str] = []
        seen: set[str] = set()
        expected = set(EDITORIAL_DIMENSIONS)
        for index, raw in enumerate(scores):
            if not isinstance(raw, dict):
                invalid.append({"index": index, "reason": "dimension-score-not-object"})
                continue
            dimension = str(raw.get("dimension") or "")
            winner = str(raw.get("winnerCandidateId") or "")
            reason = str(raw.get("reason") or "").strip()
            actual.append(dimension)
            if dimension not in expected:
                invalid.append({"index": index, "dimension": dimension, "reason": "unknown-dimension"})
            elif dimension in seen:
                duplicates.append(dimension)
            else:
                seen.add(dimension)
            if winner not in known:
                invalid.append({"index": index, "dimension": dimension, "reason": "unknown-dimension-winner"})
            if not reason:
                invalid.append({"index": index, "dimension": dimension, "reason": "empty-dimension-reason"})
        missing = [item for item in EDITORIAL_DIMENSIONS if item not in seen]
        return {
            "expectedDimensions": list(EDITORIAL_DIMENSIONS),
            "actualDimensions": actual,
            "missingDimensions": missing,
            "duplicateDimensions": duplicates,
            "invalidDimensions": invalid,
            "complete": not missing and not duplicates and not invalid and len(scores) == len(EDITORIAL_DIMENSIONS),
        }


def _pair_payload(pair: tuple[str, str]) -> dict[str, str]:
    return {"leftCandidateId": pair[0], "rightCandidateId": pair[1]}


__all__ = (
    "EDITORIAL_DIMENSIONS",
    "PairwiseComparisonIdentityPolicy",
    "PairwiseComparisonIdentityTrace",
    "PairwisePayloadValidationError",
)
