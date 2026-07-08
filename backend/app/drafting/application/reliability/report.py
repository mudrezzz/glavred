"""Owner: drafting.application.reliability

Used by: DraftRun provider reliability CLI and diagnostics.
Does not own: DraftRun execution, AiRun persistence, provider adapters, or roadmap mutation.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.app.domain.ai_run import AiRun
from backend.app.domain.draft_run import DraftRun
from backend.app.drafting.application.reliability.aggregator import ProviderReliabilityAggregator
from backend.app.drafting.application.reliability.contracts import (
    OperationReliabilityEvent,
    OperationReliabilitySummary,
    ProviderReliabilityRemediationItem,
    ReliabilitySignalCoverageRecord,
)
from backend.app.drafting.application.reliability.extractor import DraftRunReliabilityExtractor
from backend.app.drafting.application.reliability.remediation import ProviderReliabilityRemediationPolicy
from backend.app.drafting.application.reliability.signal_coverage import ReliabilitySignalCoverageExtractor


@dataclass(frozen=True)
class DraftRunProviderReliabilityReport:
    """Trace-safe cross-run reliability report."""

    run_ids: tuple[str, ...]
    events: tuple[OperationReliabilityEvent, ...]
    operation_summaries: tuple[OperationReliabilitySummary, ...]
    remediation_items: tuple[ProviderReliabilityRemediationItem, ...]
    signal_coverage: tuple[ReliabilitySignalCoverageRecord, ...]

    @property
    def conclusion_status(self) -> str:
        if len(self.run_ids) < 2:
            return "insufficientData"
        decisions = {item.decision for item in self.remediation_items}
        if "fixBeforeTrustingQuality" in decisions:
            return "requiresFixBeforeTrustingQuality"
        if "fixBacklogSlice" in decisions:
            return "requiresBacklogFix"
        if {"watchWithMoreRuns", "needsManualReview"}.intersection(decisions):
            return "watch"
        return "cleanOrNormallyRecovered"

    def to_payload(self) -> dict[str, Any]:
        return {
            "version": "draft-run-provider-reliability-v1",
            "runIds": list(self.run_ids),
            "summary": {
                "runCount": len(self.run_ids),
                "eventCount": len(self.events),
                "operationGroupCount": len(self.operation_summaries),
                "remediationItemCount": len(self.remediation_items),
                "conclusionStatus": self.conclusion_status,
                "outcomeCounts": self._outcome_counts(),
                "incidentCounts": self._incident_counts(),
            },
            "signalCoverage": self._signal_coverage_payload(),
            "operationSummaries": [item.to_payload() for item in self.operation_summaries],
            "remediationItems": [item.to_payload() for item in self.remediation_items],
            "events": [item.to_payload() for item in self.events],
        }

    def to_markdown(self) -> str:
        payload = self.to_payload()
        summary = payload["summary"]
        lines = [
            "# DraftRun Provider Reliability Report",
            "",
            "## Technical health",
            f"- runs: {summary['runCount']}",
            f"- events: {summary['eventCount']}",
            f"- conclusion: `{summary['conclusionStatus']}`",
            "",
            "## Signal coverage",
            f"- raw structured signals: {payload['signalCoverage']['summary']['totalSignals']}",
            f"- covered: {payload['signalCoverage']['summary']['coveredSignals']}",
            f"- ignored with reason: {payload['signalCoverage']['summary']['ignoredSignals']}",
            "",
            "## Provider recovery",
        ]
        lines.extend(f"- {key}: {value}" for key, value in summary["outcomeCounts"].items())
        lines.extend(["", "## Operation hotspots"])
        for item in self.operation_summaries:
            if item.outcome_counts == {"clean": item.event_count}:
                continue
            lines.append(
                f"- `{item.operation_id}` / `{item.model}`: outcomes={item.outcome_counts}; incidents={item.incident_counts}"
            )
        if len(lines) and lines[-1] == "## Operation hotspots":
            lines.append("- no non-clean operation groups")
        lines.extend(["", "## Remediation ledger"])
        if not self.remediation_items:
            lines.append("- no remediation items")
        for item in self.remediation_items:
            lines.append(
                f"- `{item.decision}` for `{item.operation_id}`: {item.proposed_fix} "
                f"(runs: {', '.join(item.affected_run_ids)})"
            )
        return "\n".join(lines) + "\n"

    def _outcome_counts(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for event in self.events:
            result[event.outcome] = result.get(event.outcome, 0) + 1
        return dict(sorted(result.items()))

    def _incident_counts(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for event in self.events:
            for incident in event.incident_types:
                result[incident] = result.get(incident, 0) + 1
        return dict(sorted(result.items()))

    def _signal_coverage_payload(self) -> dict[str, Any]:
        covered = [item for item in self.signal_coverage if item.coverage_status == "covered"]
        ignored = [item for item in self.signal_coverage if item.coverage_status == "ignored"]
        signal_counts: dict[str, int] = {}
        ignored_reason_counts: dict[str, int] = {}
        for item in self.signal_coverage:
            signal_counts[item.signal_type] = signal_counts.get(item.signal_type, 0) + 1
            if item.coverage_status == "ignored":
                ignored_reason_counts[item.reason] = ignored_reason_counts.get(item.reason, 0) + 1
        return {
            "summary": {
                "totalSignals": len(self.signal_coverage),
                "coveredSignals": len(covered),
                "ignoredSignals": len(ignored),
                "signalCounts": dict(sorted(signal_counts.items())),
                "ignoredReasonCounts": dict(sorted(ignored_reason_counts.items())),
            },
            "records": [item.to_payload() for item in self.signal_coverage],
        }


class DraftRunProviderReliabilityReporter:
    """Builds cross-run reports from DraftRun and AiRun records."""

    def __init__(
        self,
        *,
        extractor: DraftRunReliabilityExtractor | None = None,
        aggregator: ProviderReliabilityAggregator | None = None,
        remediation: ProviderReliabilityRemediationPolicy | None = None,
        signal_coverage: ReliabilitySignalCoverageExtractor | None = None,
    ) -> None:
        self._extractor = extractor or DraftRunReliabilityExtractor()
        self._aggregator = aggregator or ProviderReliabilityAggregator()
        self._remediation = remediation or ProviderReliabilityRemediationPolicy()
        self._signal_coverage = signal_coverage or ReliabilitySignalCoverageExtractor()

    def build(
        self,
        runs: list[DraftRun],
        *,
        ai_runs_by_draft_run_id: dict[str, list[AiRun]] | None = None,
    ) -> DraftRunProviderReliabilityReport:
        ai_runs_by_draft_run_id = ai_runs_by_draft_run_id or {}
        events: list[OperationReliabilityEvent] = []
        coverage: list[ReliabilitySignalCoverageRecord] = []
        for run in runs:
            run_ai_runs = ai_runs_by_draft_run_id.get(run.id, [])
            run_events = self._extractor.from_draft_run(run, run_ai_runs)
            events.extend(run_events)
            coverage.extend(self._signal_coverage.records(run, ai_runs=run_ai_runs, events=run_events))
        summaries = self._aggregator.summarize(events)
        remediation_items = self._remediation.remediation_items(summaries, run_count=len(runs))
        return DraftRunProviderReliabilityReport(
            run_ids=tuple(run.id for run in runs),
            events=tuple(events),
            operation_summaries=tuple(summaries),
            remediation_items=tuple(remediation_items),
            signal_coverage=tuple(coverage),
        )
