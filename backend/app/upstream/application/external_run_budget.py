"""Owner: upstream.application

Used by: RadarRun orchestration and governed upstream provider operations.
Does not own: provider transport, triage decisions, URL reading, persistence, or DraftRun.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations


class UpstreamRadarRunBudgetPolicy:
    def for_mode(self, mode: str) -> dict[str, int]:
        limits = {
            "maxOperations": 10,
            "maxInternalItems": 0,
            "maxExternalQueries": 3,
            "maxUrlReads": 2,
            "maxFoundMaterials": 2,
            "maxProviderInputChars": 12000,
            "maxProviderInputTokens": 3000,
            "maxResultsPerQuery": 5,
        }
        if mode == "smoke":
            limits.update(
                maxOperations=4,
                maxExternalQueries=1,
                maxUrlReads=1,
                maxFoundMaterials=1,
                maxProviderInputChars=4000,
                maxProviderInputTokens=1000,
                maxResultsPerQuery=3,
            )
        elif mode == "full":
            limits.update(
                maxOperations=16,
                maxExternalQueries=5,
                maxUrlReads=4,
                maxFoundMaterials=4,
                maxProviderInputChars=20000,
                maxProviderInputTokens=5000,
                maxResultsPerQuery=8,
            )
        return {
            **limits,
            "usedOperations": 0,
            "usedInternalItems": 0,
            "usedExternalQueries": 0,
            "usedUrlReads": 0,
            "usedFoundMaterials": 0,
            "usedProviderInputChars": 0,
            "usedProviderInputTokens": 0,
        }


_POLICY = UpstreamRadarRunBudgetPolicy()
budget_for_mode = _POLICY.for_mode


__all__ = ("UpstreamRadarRunBudgetPolicy", "budget_for_mode")
