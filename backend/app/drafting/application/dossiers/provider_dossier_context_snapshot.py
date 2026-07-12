"""Owner: drafting.application.dossiers

Used by: provider-heavy service unit and compatibility paths without a progress sink.
Does not own: persistence, provider calls, dossier policy, or hidden runtime state.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from typing import Any

from backend.app.drafting.application.context.draft_run_context_access import DraftRunContextAccessService


class ProviderDossierContextSnapshotFactory:
    """Creates deterministic context access from explicit already-owned artifacts."""

    def access(
        self,
        *,
        draft_artifact: dict[str, Any] | None = None,
        validation_report: dict[str, Any] | None = None,
        context_artifact: dict[str, Any] | None = None,
        rule_pack: dict[str, Any] | None = None,
        material_plan: dict[str, Any] | None = None,
        review_context: dict[str, Any] | None = None,
    ) -> DraftRunContextAccessService:
        context = context_artifact or {}
        validation = dict(validation_report or {})
        if review_context is not None:
            validation["reviewContext"] = review_context
        return DraftRunContextAccessService.from_snapshot(
            {
                "runId": "explicit-artifact-snapshot",
                "steps": {
                    "postContract": context.get("postContract") or {},
                    "publicEvidence": {"enrichedSourceLedger": context.get("sourceLedger") or {}},
                    "rulePack": rule_pack or {},
                    "materialPlan": {"materialPlan": material_plan or {}},
                    "draft": draft_artifact or {},
                    "validation": validation,
                },
            }
        )


__all__ = ("ProviderDossierContextSnapshotFactory",)
