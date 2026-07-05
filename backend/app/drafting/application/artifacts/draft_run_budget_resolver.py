"""Owner: drafting.application.artifacts

Used by: DraftRun artifact migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

import json
from dataclasses import replace
from typing import Any

from backend.app.domain.draft_run_budget import (
    DraftRunBudget,
    DraftRunBudgetCaps,
    DraftRunExecutionMode,
    DraftRunResearchDepth,
)
from backend.app.settings import BackendSettings, get_settings


DEFAULT_BUDGETS: dict[DraftRunResearchDepth, DraftRunBudgetCaps] = {
    DraftRunResearchDepth.LIGHT: DraftRunBudgetCaps(3, 1, 1, 3, 5, 8, 8, 3, 3),
    DraftRunResearchDepth.STANDARD: DraftRunBudgetCaps(5, 3, 2, 5, 12, 18, 12, 3, 3),
    DraftRunResearchDepth.DEEP: DraftRunBudgetCaps(8, 5, 4, 6, 24, 36, 18, 3, 3),
    DraftRunResearchDepth.MARKET_RESEARCH: DraftRunBudgetCaps(12, 8, 6, 8, 40, 60, 24, 3, 3),
}

SMOKE_CAPS = DraftRunBudgetCaps(3, 1, 1, 2, 3, 5, 8, 2, 1)

CAP_KEYS = {
    "maxResearchTasks": "max_research_tasks",
    "maxSearchTasks": "max_search_tasks",
    "maxUrlReads": "max_url_reads",
    "maxSearchResultsPerTask": "max_search_results_per_task",
    "maxAcceptedEvidenceItems": "max_accepted_evidence_items",
    "maxExternalClaims": "max_external_claims",
    "maxUsableEvidenceCandidates": "max_usable_evidence_candidates",
    "maxDraftCandidates": "max_draft_candidates",
    "maxRevisionIterations": "max_revision_iterations",
}


class DraftRunBudgetResolverComponent:
    """Owns migrated helper behavior; module-level aliases remain compatibility-only."""

    @staticmethod
    def resolve_draft_run_budget(context_artifact: dict[str, Any], settings: BackendSettings | None = None) -> DraftRunBudget:
        settings = settings or get_settings()
        depth = _research_depth(context_artifact)
        mode = _execution_mode(settings.draft_run_execution_mode)
        caps = _apply_overrides(DEFAULT_BUDGETS[depth], settings.draft_research_budget_overrides, depth.value)
        caps = replace(caps, max_revision_iterations=max(1, int(settings.draft_revision_max_iterations or 1)))
        if mode == DraftRunExecutionMode.SMOKE:
            caps = _min_caps(caps, _apply_overrides(SMOKE_CAPS, settings.draft_run_smoke_budget_overrides, "smoke"))
        return DraftRunBudget(research_depth=depth, execution_mode=mode, caps=caps, source="fabula+executionMode")

    @staticmethod
    def budget_from_context(context_artifact: dict[str, Any] | None) -> DraftRunBudget:
        payload = context_artifact.get("draftRunBudget") if isinstance(context_artifact, dict) else None
        if not isinstance(payload, dict):
            return resolve_draft_run_budget(context_artifact or {})
        caps_payload = payload.get("caps") if isinstance(payload.get("caps"), dict) else {}
        caps = _apply_cap_payload(DEFAULT_BUDGETS[_research_depth({"fabula": {"researchDepth": payload.get("researchDepth")}})], caps_payload)
        return DraftRunBudget(
            research_depth=_depth_value(payload.get("researchDepth")),
            execution_mode=_execution_mode(payload.get("executionMode")),
            caps=caps,
            source=str(payload.get("source") or "artifact"),
        )

    @staticmethod
    def _research_depth(context_artifact: dict[str, Any]) -> DraftRunResearchDepth:
        fabula = context_artifact.get("fabula") if isinstance(context_artifact.get("fabula"), dict) else {}
        return _depth_value(fabula.get("researchDepth"))

    @staticmethod
    def _depth_value(value: Any) -> DraftRunResearchDepth:
        try:
            return DraftRunResearchDepth(str(value or DraftRunResearchDepth.STANDARD.value))
        except ValueError:
            return DraftRunResearchDepth.STANDARD

    @staticmethod
    def _execution_mode(value: Any) -> DraftRunExecutionMode:
        try:
            return DraftRunExecutionMode(str(value or DraftRunExecutionMode.STANDARD.value).strip())
        except ValueError:
            return DraftRunExecutionMode.STANDARD

    @staticmethod
    def _apply_overrides(caps: DraftRunBudgetCaps, raw: str, key: str) -> DraftRunBudgetCaps:
        try:
            parsed = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            return caps
        profile = parsed.get(key) if isinstance(parsed, dict) else None
        return _apply_cap_payload(caps, profile if isinstance(profile, dict) else parsed if isinstance(parsed, dict) and key == "smoke" else {})

    @staticmethod
    def _apply_cap_payload(caps: DraftRunBudgetCaps, payload: dict[str, Any]) -> DraftRunBudgetCaps:
        updates = {}
        for payload_key, field_name in CAP_KEYS.items():
            value = payload.get(payload_key)
            if isinstance(value, int) and value > 0:
                updates[field_name] = value
        return replace(caps, **updates) if updates else caps

    @staticmethod
    def _min_caps(left: DraftRunBudgetCaps, right: DraftRunBudgetCaps) -> DraftRunBudgetCaps:
        return DraftRunBudgetCaps(**{
            field: min(getattr(left, field), getattr(right, field))
            for field in DraftRunBudgetCaps.__dataclass_fields__
        })

resolve_draft_run_budget = DraftRunBudgetResolverComponent.resolve_draft_run_budget
budget_from_context = DraftRunBudgetResolverComponent.budget_from_context
_research_depth = DraftRunBudgetResolverComponent._research_depth
_depth_value = DraftRunBudgetResolverComponent._depth_value
_execution_mode = DraftRunBudgetResolverComponent._execution_mode
_apply_overrides = DraftRunBudgetResolverComponent._apply_overrides
_apply_cap_payload = DraftRunBudgetResolverComponent._apply_cap_payload
_min_caps = DraftRunBudgetResolverComponent._min_caps


__all__ = (
    'DEFAULT_BUDGETS',
    'SMOKE_CAPS',
    'CAP_KEYS',
    'resolve_draft_run_budget',
    'budget_from_context',
    'DraftRunBudgetResolverComponent',
)
