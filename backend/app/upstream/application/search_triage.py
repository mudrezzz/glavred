"""Compatibility exports for the typed RadarRun search-triage owners.

Owner: upstream.application
Used by: legacy imports during Search Result Triage v2 migration.
Does not own: triage behavior, provider transport, persistence, or UI rendering.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from backend.app.upstream.application.search_triage_service import SearchResultTriageService
from backend.app.upstream.domain.search_triage_contracts import SearchTriageResult


__all__ = ("SearchResultTriageService", "SearchTriageResult")
