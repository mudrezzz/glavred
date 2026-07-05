"""Owner: drafting.application.evidence

Used by: DraftRun evidence migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.evidence.public_evidence_budgeting import max_search_results_per_task
from backend.app.drafting.application.evidence.public_evidence_ports import PublicEvidenceSearchTask


class PublicEvidenceQueryBuilderComponent:
    """Owns migrated helper behavior; module-level aliases remain compatibility-only."""

    @staticmethod
    def build_public_evidence_search_task(
        task: dict[str, Any],
        *,
        source_intent_artifact: dict[str, Any],
        context_artifact: dict[str, Any] | None = None,
    ) -> PublicEvidenceSearchTask:
        instruction = _clean(task.get("instruction")) or _clean(task.get("target"))
        technical_target = _clean(task.get("target"))
        source_target = _source_target(source_intent_artifact, technical_target)
        exclusions = _exclusions(source_intent_artifact)
        query_parts = [
            instruction,
            _brief_context(context_artifact or {}),
            _source_target_context(source_target),
            _exclusion_context(exclusions),
        ]
        query = "\n".join(part for part in query_parts if part)
        return PublicEvidenceSearchTask(
            query=query,
            task_id=_optional_str(task.get("id")),
            source_intent_item_id=_optional_str(task.get("sourceIntentItemId")),
            kind=_clean(task.get("kind")) or "search",
            technical_target=technical_target,
            instruction=instruction,
            source_target=source_target,
            exclusions=exclusions,
            original_task=dict(task),
            max_results=max_search_results_per_task(context_artifact),
        )

    @staticmethod
    def _brief_context(context_artifact: dict[str, Any]) -> str:
        brief = context_artifact.get("brief") if isinstance(context_artifact.get("brief"), dict) else {}
        title = _clean(brief.get("title"))
        thesis = _clean(brief.get("thesis"))
        if not title and not thesis:
            return ""
        return f"Post context: {title}. Thesis: {thesis}".strip()

    @staticmethod
    def _source_target_context(source_target: dict[str, Any] | None) -> str:
        if not source_target:
            return ""
        title = _clean(source_target.get("title")) or _clean(source_target.get("label"))
        description = _clean(source_target.get("description")) or _clean(source_target.get("target"))
        return f"Source target: {title}. {description}".strip()

    @staticmethod
    def _exclusion_context(exclusions: list[str]) -> str:
        return f"Do not use: {'; '.join(exclusions)}" if exclusions else ""

    @staticmethod
    def _source_target(source_intent_artifact: dict[str, Any], target_id: str | None) -> dict[str, Any] | None:
        if not target_id:
            return None
        research_plan = source_intent_artifact.get("researchPlan")
        targets = research_plan.get("sourceTargets") if isinstance(research_plan, dict) else None
        if not isinstance(targets, list):
            return None
        for target in targets:
            if isinstance(target, dict) and str(target.get("id") or "") == target_id:
                return target
        return None

    @staticmethod
    def _exclusions(source_intent_artifact: dict[str, Any]) -> list[str]:
        research_plan = source_intent_artifact.get("researchPlan")
        exclusions = research_plan.get("exclusions") if isinstance(research_plan, dict) else None
        if not isinstance(exclusions, list):
            return []
        return [_clean(item) for item in exclusions if _clean(item)]

    @staticmethod
    def _optional_str(value: Any) -> str | None:
        cleaned = _clean(value)
        return cleaned or None

    @staticmethod
    def _clean(value: Any) -> str:
        return " ".join(str(value or "").split())

build_public_evidence_search_task = PublicEvidenceQueryBuilderComponent.build_public_evidence_search_task
_brief_context = PublicEvidenceQueryBuilderComponent._brief_context
_source_target_context = PublicEvidenceQueryBuilderComponent._source_target_context
_exclusion_context = PublicEvidenceQueryBuilderComponent._exclusion_context
_source_target = PublicEvidenceQueryBuilderComponent._source_target
_exclusions = PublicEvidenceQueryBuilderComponent._exclusions
_optional_str = PublicEvidenceQueryBuilderComponent._optional_str
_clean = PublicEvidenceQueryBuilderComponent._clean


__all__ = (
    'build_public_evidence_search_task',
    'PublicEvidenceQueryBuilderComponent',
)
