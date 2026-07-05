"""Owner: drafting.application.evidence

Used by: DraftRun evidence migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.artifacts.draft_run_budget_resolver import budget_from_context
from backend.app.domain.draft_public_evidence import (
    PublicEvidenceAttempt,
    PublicEvidenceAttemptStatus,
    PublicEvidenceItem,
    PublicEvidenceWarning,
)


class PublicEvidenceBudgetingPolicy:
    """Owns migrated helper behavior; module-level aliases remain compatibility-only."""

    @staticmethod
    def budget_public_evidence_tasks(
        tasks: list[dict[str, Any]],
        context_artifact: dict[str, Any] | None,
    ) -> tuple[list[dict[str, Any]], list[PublicEvidenceAttempt], list[PublicEvidenceWarning], dict[str, Any]]:
        budget = budget_from_context(context_artifact)
        kept: list[dict[str, Any]] = []
        skipped: list[PublicEvidenceAttempt] = []
        counts = {"searchTasks": 0, "urlReads": 0}
        skipped_counts = {"searchTasks": 0, "urlReads": 0}
        for task in tasks:
            kind = str(task.get("kind") or "")
            cap_key = "urlReads" if kind == "readUrl" else "searchTasks" if kind in {"findPublicSources", "verifyClaim"} else ""
            if cap_key and counts[cap_key] >= _cap_for_kind(budget.to_payload()["caps"], cap_key):
                skipped.append(_skipped_attempt(task, "draft-run-budget-cap"))
                skipped_counts[cap_key] += 1
                continue
            if cap_key:
                counts[cap_key] += 1
            kept.append(task)
        warnings = [
            PublicEvidenceWarning(code="public-evidence-budget-skipped", message=f"{len(skipped)} retrieval task(s) skipped by DraftRun budget.")
        ] if skipped else []
        trace = {
            "draftRunBudget": budget.to_payload(),
            "usedCounts": {"retrievalTasks": len(kept), **counts},
            "budgetSkipped": [attempt.to_payload() for attempt in skipped],
            "capHits": {"searchTasks": skipped_counts["searchTasks"] > 0, "urlReads": skipped_counts["urlReads"] > 0},
        }
        return kept, skipped, warnings, trace

    @staticmethod
    def trim_public_evidence_items(
        items: list[PublicEvidenceItem],
        context_artifact: dict[str, Any] | None,
    ) -> tuple[list[PublicEvidenceItem], list[PublicEvidenceWarning], dict[str, Any]]:
        budget = budget_from_context(context_artifact)
        limit = budget.caps.max_accepted_evidence_items
        kept = items[:limit]
        trimmed = items[limit:]
        warnings = [
            PublicEvidenceWarning(code="public-evidence-budget-trimmed", message=f"{len(trimmed)} evidence item(s) trimmed by DraftRun budget.")
        ] if trimmed else []
        return kept, warnings, {"trimmedEvidenceItems": [item.to_payload() for item in trimmed], "acceptedEvidenceLimit": limit}

    @staticmethod
    def max_search_results_per_task(context_artifact: dict[str, Any] | None) -> int:
        return budget_from_context(context_artifact).caps.max_search_results_per_task

    @staticmethod
    def _cap_for_kind(caps: dict[str, Any], key: str) -> int:
        return int(caps.get("maxUrlReads" if key == "urlReads" else "maxSearchTasks") or 0)

    @staticmethod
    def _skipped_attempt(task: dict[str, Any], reason: str) -> PublicEvidenceAttempt:
        task_id = str(task.get("id") or task.get("sourceIntentItemId") or "unlinked")
        return PublicEvidenceAttempt(
            id=f"budget-skip-{task_id}",
            task_id=str(task.get("id")) if task.get("id") else None,
            source_intent_item_id=str(task.get("sourceIntentItemId")) if task.get("sourceIntentItemId") else None,
            kind=str(task.get("kind") or "unknown"),
            target=str(task.get("target") or task.get("instruction") or ""),
            status=PublicEvidenceAttemptStatus.SKIPPED,
            notes=[reason],
            metadata={"reason": reason},
        )

budget_public_evidence_tasks = PublicEvidenceBudgetingPolicy.budget_public_evidence_tasks
trim_public_evidence_items = PublicEvidenceBudgetingPolicy.trim_public_evidence_items
max_search_results_per_task = PublicEvidenceBudgetingPolicy.max_search_results_per_task
_cap_for_kind = PublicEvidenceBudgetingPolicy._cap_for_kind
_skipped_attempt = PublicEvidenceBudgetingPolicy._skipped_attempt


__all__ = (
    'budget_public_evidence_tasks',
    'trim_public_evidence_items',
    'max_search_results_per_task',
    'PublicEvidenceBudgetingPolicy',
)
