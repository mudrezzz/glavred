"""Owner: drafting.application.evidence

Used by: DraftRun evidence migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from backend.app.domain.draft_source_intent import (
    ResearchPlan,
    ResearchPlanTask,
    ResearchPlanTaskKind,
    SourceIntent,
    SourceIntentItem,
    SourceIntentItemKind,
)


class DeterministicSourceResearchPlanService:
    def create(self, source_intent: SourceIntent) -> ResearchPlan:
        return ResearchPlan(
            research_questions=[question for item in source_intent.items if (question := self._question(item))],
            source_targets=[target for item in source_intent.items if (target := self._target(item))],
            verification_tasks=[self._task(index + 1, item) for index, item in enumerate(source_intent.items)],
            query_candidates=[query for item in source_intent.items if (query := self._query(item))],
            exclusions=[item.instruction for item in source_intent.items if item.kind == SourceIntentItemKind.EXCLUSION],
            warnings=[*source_intent.warnings, "Deterministic plan does not execute search or fetch URLs."],
            metadata={"version": "research-plan-v1", "mode": "deterministicFallback"},
        )

    def _task(self, index: int, item: SourceIntentItem) -> ResearchPlanTask:
        kind = {
            SourceIntentItemKind.URL: ResearchPlanTaskKind.READ_URL,
            SourceIntentItemKind.EXCLUSION: ResearchPlanTaskKind.RESPECT_EXCLUSION,
            SourceIntentItemKind.PROOF_NEED: ResearchPlanTaskKind.VERIFY_CLAIM,
            SourceIntentItemKind.FRAMING_HINT: ResearchPlanTaskKind.USE_AS_FRAMING,
        }.get(item.kind, ResearchPlanTaskKind.FIND_PUBLIC_SOURCES)
        return ResearchPlanTask(
            id=f"research-task-{index}",
            kind=kind,
            source_intent_item_id=item.id,
            instruction=item.instruction,
            target=self._target(item) or item.raw,
            priority="high" if item.kind in {SourceIntentItemKind.URL, SourceIntentItemKind.PROOF_NEED} else "medium",
        )

    def _question(self, item: SourceIntentItem) -> str:
        if item.kind == SourceIntentItemKind.EXCLUSION:
            return ""
        if item.kind == SourceIntentItemKind.URL:
            return f"What usable evidence is present at {item.instruction}?"
        if item.kind == SourceIntentItemKind.PROOF_NEED:
            return f"What public evidence confirms or weakens: {item.instruction}?"
        return f"What public context helps evaluate: {item.instruction}?"

    def _target(self, item: SourceIntentItem) -> str:
        if item.kind == SourceIntentItemKind.URL:
            return item.instruction
        if item.kind == SourceIntentItemKind.NAMED_SOURCE:
            return item.instruction
        if item.kind == SourceIntentItemKind.RESEARCH_REQUEST:
            return "credible public experts, reports, interviews, or primary sources"
        if item.kind == SourceIntentItemKind.PROOF_NEED:
            return "public data, benchmarks, reports, or primary evidence"
        if item.kind == SourceIntentItemKind.FRAMING_HINT:
            return "framing context only"
        return ""

    def _query(self, item: SourceIntentItem) -> str:
        if item.kind in {SourceIntentItemKind.RESEARCH_REQUEST, SourceIntentItemKind.PROOF_NEED, SourceIntentItemKind.NAMED_SOURCE}:
            return item.instruction
        return ""


DeterministicSourceResearchPlanFallbackService = DeterministicSourceResearchPlanService


__all__ = (
    'DeterministicSourceResearchPlanService',
    'DeterministicSourceResearchPlanFallbackService',
)
