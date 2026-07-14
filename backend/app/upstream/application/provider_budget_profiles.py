"""Owner: upstream.application

Used by: upstream provider operations to resolve direct input and run budget limits.
Does not own: provider transport, prompt construction, RadarRun orchestration, or DraftRun budgets.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UpstreamProviderBudgetProfile:
    id: str
    operation_id: str
    execution_mode: str
    max_query_chars: int
    max_provider_input_chars: int
    max_message_chars: int
    max_approx_tokens: int
    max_run_input_chars: int
    max_run_approx_tokens: int
    max_results_per_query: int


class UpstreamProviderBudgetProfileRegistry:
    _RUN_LIMITS = {
        "smoke": (4000, 1000, 3),
        "standard": (12000, 3000, 5),
        "full": (20000, 5000, 8),
    }

    def resolve(
        self,
        *,
        operation_id: str,
        execution_mode: str,
        configured_max_results: int,
    ) -> UpstreamProviderBudgetProfile:
        if operation_id != "openWebQuery":
            raise KeyError(f"Unknown upstream provider budget operation: {operation_id}")
        mode = execution_mode if execution_mode in self._RUN_LIMITS else "standard"
        run_chars, run_tokens, profile_results = self._RUN_LIMITS[mode]
        configured = max(0, int(configured_max_results))
        return UpstreamProviderBudgetProfile(
            id=f"upstream-open-web-query-v1-{mode}",
            operation_id=operation_id,
            execution_mode=mode,
            max_query_chars=1000,
            max_provider_input_chars=1500,
            max_message_chars=4000,
            max_approx_tokens=1000,
            max_run_input_chars=run_chars,
            max_run_approx_tokens=run_tokens,
            max_results_per_query=min(profile_results, configured) if configured else profile_results,
        )


__all__ = ("UpstreamProviderBudgetProfile", "UpstreamProviderBudgetProfileRegistry")
