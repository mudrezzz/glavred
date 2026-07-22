"""Compatibility exports for RadarRun external payload owners.

Owner: upstream.application
Used by: existing external RadarRun imports and tests.
Does not own: payload behavior, budgets, provider transport, persistence, or DraftRun.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from backend.app.upstream.application.external_run_budget import budget_for_mode
from backend.app.upstream.application.external_run_payloads import (
    UpstreamRadarPayloadFactory,
    material_from_raw,
    material_from_read,
    now_iso,
    operation,
    raw_result,
    safe_error,
    stable_slug,
    warnings_for,
)


__all__ = (
    "UpstreamRadarPayloadFactory",
    "budget_for_mode",
    "material_from_raw",
    "material_from_read",
    "now_iso",
    "operation",
    "raw_result",
    "safe_error",
    "stable_slug",
    "warnings_for",
)
