"""Owner: drafting.application.reliability

Used by: DraftRun provider reliability report assembly.
Does not own: event extraction, remediation policy, persistence, or provider behavior.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from collections import Counter, defaultdict

from backend.app.drafting.application.reliability.contracts import (
    OperationReliabilityEvent,
    OperationReliabilitySummary,
)


class ProviderReliabilityAggregator:
    """Groups operation reliability events by operation, provider, model, and mode."""

    def summarize(self, events: list[OperationReliabilityEvent]) -> list[OperationReliabilitySummary]:
        grouped: dict[tuple[str, str, str, str, str, str], list[OperationReliabilityEvent]] = defaultdict(list)
        for event in events:
            grouped[event.group_key()].append(event)

        summaries = [self._summary(key, items) for key, items in grouped.items()]
        return sorted(summaries, key=lambda item: (item.step_key, item.operation_id, item.provider, item.model))

    def _summary(
        self,
        key: tuple[str, str, str, str, str, str],
        events: list[OperationReliabilityEvent],
    ) -> OperationReliabilitySummary:
        operation_id, step_key, provider, model, model_role, execution_mode = key
        outcome_counts = Counter(event.outcome for event in events)
        incident_counts: Counter[str] = Counter()
        for event in events:
            incident_counts.update(event.incident_types)
        return OperationReliabilitySummary(
            operation_id=operation_id,
            step_key=step_key,
            provider=provider,
            model=model,
            model_role=model_role,
            execution_mode=execution_mode,
            run_ids=tuple(sorted({event.run_id for event in events})),
            event_count=len(events),
            outcome_counts=dict(sorted(outcome_counts.items())),
            incident_counts=dict(sorted(incident_counts.items())),
            total_attempts=sum(event.attempt_count for event in events),
        )
