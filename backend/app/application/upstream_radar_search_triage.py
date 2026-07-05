"""Compatibility shim for upstream radar search triage."""

from backend.app.upstream.application.search_triage import (
    UpstreamSearchTriagePolicy,
    canonical_url,
    result_domain,
    score_search_result,
    select_results_for_read,
)

__all__ = (
    "UpstreamSearchTriagePolicy",
    "canonical_url",
    "result_domain",
    "score_search_result",
    "select_results_for_read",
)
