"""Owner: drafting.application.artifacts

Used by: DraftRun artifact migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.artifacts.draft_run_budget_resolver import budget_from_context


class SourceLedgerBudgetingPolicy:
    """Owns migrated helper behavior; module-level aliases remain compatibility-only."""

    @staticmethod
    def apply_external_claim_budget(
        *,
        source_ledger: dict[str, Any],
        context_artifact: dict[str, Any],
    ) -> dict[str, Any]:
        budget = budget_from_context(context_artifact)
        claims = [item for item in source_ledger.get("claims", []) if isinstance(item, dict)] if isinstance(source_ledger.get("claims"), list) else []
        external = [claim for claim in claims if claim.get("type") == "externalEvidenceClaim"]
        if len(external) <= budget.caps.max_external_claims:
            return {**source_ledger, "draftRunBudget": budget.to_payload()}
        keep_ids = {claim.get("id") for claim in external[:budget.caps.max_external_claims]}
        trimmed = [claim for claim in external if claim.get("id") not in keep_ids]
        kept_claims = [claim for claim in claims if claim.get("type") != "externalEvidenceClaim" or claim.get("id") in keep_ids]
        metadata = source_ledger.get("metadata") if isinstance(source_ledger.get("metadata"), dict) else {}
        warnings = source_ledger.get("warnings") if isinstance(source_ledger.get("warnings"), list) else []
        return {
            **source_ledger,
            "claims": kept_claims,
            "warnings": [*warnings, {
                "id": "external-evidence-budget-trimmed",
                "title": "External evidence claims trimmed by DraftRun budget",
                "detail": f"{len(trimmed)} external claim(s) were kept out of the active ledger.",
                "source": "draftRunBudget",
            }],
            "metadata": {**metadata, "externalClaimCount": len(external[:budget.caps.max_external_claims]), "trimmedExternalClaimCount": len(trimmed)},
            "budgetTrimmedExternalClaims": trimmed,
            "draftRunBudget": budget.to_payload(),
        }

apply_external_claim_budget = SourceLedgerBudgetingPolicy.apply_external_claim_budget


__all__ = (
    'apply_external_claim_budget',
    'SourceLedgerBudgetingPolicy',
)
