from __future__ import annotations

import json

import pytest

from backend.app.drafting.application.revision.draft_pairwise_ranking_prompts import PairwiseRankingPromptBuilder
from backend.app.drafting.application.revision.pairwise_comparison_identity import (
    EDITORIAL_DIMENSIONS,
    PairwiseComparisonIdentityPolicy,
    PairwisePayloadValidationError,
)


def test_identity_policy_accepts_complete_matrices_for_two_three_and_four_candidates() -> None:
    policy = PairwiseComparisonIdentityPolicy()
    for count, expected_count in ((2, 1), (3, 3), (4, 6)):
        candidate_ids = [f"candidate-{index}" for index in range(count)]
        payload = _payload(candidate_ids)

        trace = policy.validate(payload, candidate_ids)

        assert trace.complete is True
        assert len(trace.expected_pairs) == expected_count
        assert trace.actual_pair_count == expected_count


@pytest.mark.parametrize(
    ("comparison", "reason"),
    [
        ({"leftCandidateId": "", "rightCandidateId": "b", "winnerCandidateId": "b"}, "blank-candidate-identity"),
        ({"leftCandidateId": "a", "rightCandidateId": "missing", "winnerCandidateId": "a"}, "unknown-pair-candidate"),
        ({"leftCandidateId": "a", "rightCandidateId": "a", "winnerCandidateId": "a"}, "self-pair"),
        ({"leftCandidateId": "a", "rightCandidateId": "b", "winnerCandidateId": "c"}, "winner-outside-pair"),
    ],
)
def test_identity_policy_rejects_invalid_pair_identity(comparison: dict[str, str], reason: str) -> None:
    payload = _payload(["a", "b"])
    payload["comparisons"] = [comparison]

    trace = PairwiseComparisonIdentityPolicy().evaluate(payload, ["a", "b"])

    assert trace.complete is False
    assert trace.invalid_pairs[0]["reason"] == reason


def test_identity_policy_treats_reversed_pair_as_duplicate_and_reports_missing_pair() -> None:
    payload = _payload(["a", "b", "c"])
    payload["comparisons"] = [payload["comparisons"][0], {"leftCandidateId": "b", "rightCandidateId": "a", "winnerCandidateId": "b", "reason": "duplicate"}]

    trace = PairwiseComparisonIdentityPolicy().evaluate(payload, ["a", "b", "c"])

    assert trace.complete is False
    assert trace.duplicate_pairs[0]["reason"] == "duplicate-unordered-pair"
    assert len(trace.missing_pairs) == 2


def test_identity_policy_requires_seven_unique_dimension_scores() -> None:
    payload = _payload(["a", "b"])
    payload["editorialDimensionScores"] = [
        {"dimension": "ideaStrength", "winnerCandidateId": "a", "reason": ""},
        {"dimension": "ideaStrength", "winnerCandidateId": "missing", "reason": "duplicate"},
    ]

    with pytest.raises(PairwisePayloadValidationError) as error:
        PairwiseComparisonIdentityPolicy().validate(payload, ["a", "b"])

    coverage = error.value.to_payload()["dimensionCoverage"]
    assert "ideaStrength" in coverage["duplicateDimensions"]
    assert "tension" in coverage["missingDimensions"]
    assert coverage["complete"] is False


def test_prompt_contains_exact_expected_pairs_and_identity_shape() -> None:
    messages = PairwiseRankingPromptBuilder().build_from_provider_input(
        provider_input={"candidates": [{"id": "a"}, {"id": "b"}, {"id": "c"}]},
    )

    payload = json.loads(messages[1]["content"])

    assert payload["comparisonContract"]["expectedPairCount"] == 3
    assert payload["comparisonContract"]["expectedPairs"] == [
        {"leftCandidateId": "a", "rightCandidateId": "b"},
        {"leftCandidateId": "a", "rightCandidateId": "c"},
        {"leftCandidateId": "b", "rightCandidateId": "c"},
    ]
    assert set(payload["requiredJson"]["comparisons"][0]) == {
        "leftCandidateId", "rightCandidateId", "winnerCandidateId", "reason", "decisiveFactors"
    }


def _payload(candidate_ids: list[str]) -> dict[str, object]:
    pairs = PairwiseComparisonIdentityPolicy().expected_pairs(candidate_ids)
    return {
        "winnerCandidateId": candidate_ids[0],
        "reason": "best",
        "comparisons": [
            {
                "leftCandidateId": left,
                "rightCandidateId": right,
                "winnerCandidateId": left,
                "reason": "better",
                "decisiveFactors": ["clearer"],
            }
            for left, right in pairs
        ],
        "editorialDimensionScores": [
            {"dimension": dimension, "winnerCandidateId": candidate_ids[0], "reason": "better"}
            for dimension in EDITORIAL_DIMENSIONS
        ],
    }
