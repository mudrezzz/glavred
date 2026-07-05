"""Owner: drafting.application.evidence

Used by: DraftRun evidence migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.artifacts.draft_run_budget_resolver import budget_from_context


class SourceResearchBudgetingPolicy:
    """Owns migrated helper behavior; module-level aliases remain compatibility-only."""

    @staticmethod
    def apply_source_research_budget(
        *,
        artifact_payload: dict[str, Any],
        context_artifact: dict[str, Any],
    ) -> dict[str, Any]:
        budget = budget_from_context(context_artifact)
        plan = artifact_payload.get("researchPlan")
        if not isinstance(plan, dict):
            return artifact_payload
        tasks = _dicts(plan.get("verificationTasks"))
        kept, skipped = _cap_tasks(tasks, budget.caps.max_research_tasks)
        search_kept, search_skipped = _cap_kind(kept, {"findPublicSources", "verifyClaim"}, budget.caps.max_search_tasks)
        url_kept, url_skipped = _cap_kind(search_kept, {"readUrl"}, budget.caps.max_url_reads)
        skipped_tasks = [*skipped, *search_skipped, *url_skipped]
        budgeted_plan = {**plan, "verificationTasks": url_kept}
        budget_trace = {
            "draftRunBudget": budget.to_payload(),
            "usedCounts": {
                "researchTasks": len(url_kept),
                "searchTasks": len([task for task in url_kept if task.get("kind") in {"findPublicSources", "verifyClaim"}]),
                "urlReads": len([task for task in url_kept if task.get("kind") == "readUrl"]),
            },
            "budgetSkipped": [_skip_payload(task, index) for index, task in enumerate(skipped_tasks, start=1)],
            "capHits": {
                "researchTasks": len(tasks) > budget.caps.max_research_tasks,
                "searchTasks": len(search_skipped) > 0,
                "urlReads": len(url_skipped) > 0,
            },
        }
        return {**artifact_payload, "researchPlan": budgeted_plan, "draftRunBudget": budget.to_payload(), "budgetTrace": budget_trace}

    @staticmethod
    def _cap_tasks(tasks: list[dict[str, Any]], limit: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        return tasks[:limit], tasks[limit:]

    @staticmethod
    def _cap_kind(
        tasks: list[dict[str, Any]],
        kinds: set[str],
        limit: int,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        kept: list[dict[str, Any]] = []
        skipped: list[dict[str, Any]] = []
        count = 0
        for task in tasks:
            if task.get("kind") not in kinds:
                kept.append(task)
                continue
            count += 1
            if count <= limit:
                kept.append(task)
            else:
                skipped.append(task)
        return kept, skipped

    @staticmethod
    def _skip_payload(task: dict[str, Any], index: int) -> dict[str, Any]:
        return {
            "id": str(task.get("id") or f"budget-skip-{index}"),
            "kind": str(task.get("kind") or "unknown"),
            "target": str(task.get("target") or task.get("instruction") or ""),
            "reason": "draft-run-budget-cap",
        }

    @staticmethod
    def _dicts(value: Any) -> list[dict[str, Any]]:
        return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []

apply_source_research_budget = SourceResearchBudgetingPolicy.apply_source_research_budget
_cap_tasks = SourceResearchBudgetingPolicy._cap_tasks
_cap_kind = SourceResearchBudgetingPolicy._cap_kind
_skip_payload = SourceResearchBudgetingPolicy._skip_payload
_dicts = SourceResearchBudgetingPolicy._dicts


__all__ = (
    'apply_source_research_budget',
    'SourceResearchBudgetingPolicy',
)
