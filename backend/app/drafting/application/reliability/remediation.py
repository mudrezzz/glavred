"""Owner: drafting.application.reliability

Used by: DraftRun provider reliability analytics.
Does not own: roadmap mutation, provider configuration, prompt repair, or model policy.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from backend.app.drafting.application.reliability.contracts import (
    OperationReliabilitySummary,
    ProviderReliabilityRemediationItem,
)


class ProviderReliabilityRemediationPolicy:
    """Maps observed reliability signals to explicit follow-up decisions."""

    def remediation_items(
        self,
        summaries: list[OperationReliabilitySummary],
        *,
        run_count: int,
    ) -> list[ProviderReliabilityRemediationItem]:
        items = [self._item(summary, run_count) for summary in summaries if not self._is_clean(summary)]
        return sorted(items, key=lambda item: (item.blocking_level, item.step_key, item.operation_id))

    def _item(
        self,
        summary: OperationReliabilitySummary,
        run_count: int,
    ) -> ProviderReliabilityRemediationItem:
        counters = {**summary.outcome_counts, **{f"incident:{key}": value for key, value in summary.incident_counts.items()}}
        decision, blocking = self._decision(summary, run_count)
        return ProviderReliabilityRemediationItem(
            decision=decision,
            operation_id=summary.operation_id,
            step_key=summary.step_key,
            provider=summary.provider,
            model=summary.model,
            affected_run_ids=summary.run_ids,
            evidence_counters=counters,
            probable_cause=self._probable_cause(summary),
            proposed_fix=self._proposed_fix(decision, summary),
            owner=self._owner(summary),
            recommended_slice=self._recommended_slice(decision, summary),
            blocking_level=blocking,
        )

    def _decision(self, summary: OperationReliabilitySummary, run_count: int) -> tuple[str, str]:
        outcomes = summary.outcome_counts
        incidents = summary.incident_counts
        if outcomes.get("failed") or outcomes.get("openCritical") or outcomes.get("payloadTooLarge"):
            return "fixBeforeTrustingQuality", "qualityGate"
        if outcomes.get("finalGateWarning") or outcomes.get("contextOverBudget"):
            return "watchWithMoreRuns" if run_count < 3 else "fixBacklogSlice", "nextLiveProof"
        if outcomes.get("fallbackRecovered") or outcomes.get("degraded"):
            return "watchWithMoreRuns" if run_count < 3 else "fixBacklogSlice", "nextLiveProof"
        if outcomes.get("backupRecovered"):
            return "watchWithMoreRuns", "none"
        if outcomes.get("retryRecovered"):
            severe_incidents = {"providerTimeout", "provider5xx", "schemaFailure"}
            if severe_incidents.intersection(incidents) or run_count < 3:
                return "watchWithMoreRuns", "none"
            return "noActionExpected", "none"
        return "needsManualReview", "nextLiveProof"

    def _probable_cause(self, summary: OperationReliabilitySummary) -> str:
        incidents = set(summary.incident_counts)
        outcomes = set(summary.outcome_counts)
        if "openCritical" in outcomes:
            return "validation-open-critical"
        if "finalGateWarning" in outcomes:
            return "final-gate-warning"
        if "payloadTooLarge" in outcomes or "contextOverBudget" in outcomes:
            return "provider-input-budget"
        if "fallbackRecovered" in outcomes:
            return "provider-path-fallback"
        if "backupRecovered" in outcomes:
            return "primary-model-recovered-by-backup"
        if "providerTimeout" in incidents:
            return "provider-timeout"
        if "malformedJson" in incidents:
            return "provider-malformed-json"
        if "schemaFailure" in incidents:
            return "json-schema-repair"
        return "mixed-provider-reliability-signal"

    def _proposed_fix(self, decision: str, summary: OperationReliabilitySummary) -> str:
        if decision == "noActionExpected":
            return "No product fix. Keep counting retry frequency across later runs."
        if decision == "watchWithMoreRuns":
            return "Collect more live runs before changing prompt, model, or budget policy."
        if summary.outcome_counts.get("openCritical"):
            return "Add a quality/fidelity repair slice for unresolved validation criticals before trusting publication quality."
        if summary.outcome_counts.get("finalGateWarning"):
            return "Review final-quality warning lifecycle and decide whether repair, accepted risk, or stronger gate policy is needed."
        if self._is_evidence_repair(summary):
            return "Repair evidence interpretation timeout/fallback behavior and strengthen evidence fidelity thresholds."
        if self._is_validation_repair(summary):
            return "Repair validation/revision/final-gate loop semantics so provider incidents and critical findings cannot end as trusted quality."
        if summary.outcome_counts.get("fallbackRecovered") or summary.outcome_counts.get("degraded"):
            return "Inspect operation prompt/input budget/model reliability and add a targeted repair slice."
        if summary.outcome_counts.get("failed"):
            return "Fix the failing operation path or explicitly block the final DraftRun result."
        return "Review this operation manually and convert the finding into a concrete repair slice."

    def _owner(self, summary: OperationReliabilitySummary) -> str:
        if summary.operation_id.startswith("qualityFidelity"):
            return "drafting.application.quality"
        if summary.step_key in {"validation", "quality"}:
            return "drafting.application.validation"
        return f"drafting.application.{summary.step_key}"

    def _recommended_slice(self, decision: str, summary: OperationReliabilitySummary) -> str:
        if decision in {"noActionExpected", "watchWithMoreRuns"}:
            return "2.17.4.6.1.3"
        if self._is_evidence_repair(summary):
            return "2.17.4.6.1.3.1"
        if self._is_validation_repair(summary):
            return "2.17.4.6.1.3.2"
        return "2.17.4.6.1.3.3"

    def _is_clean(self, summary: OperationReliabilitySummary) -> bool:
        return set(summary.outcome_counts) == {"clean"}

    def _is_evidence_repair(self, summary: OperationReliabilitySummary) -> bool:
        return (
            summary.operation_id == "qualityFidelity:evidenceFidelity"
            or summary.operation_id == "evidenceInterpretation"
            or summary.step_key == "evidenceInterpretation"
        )

    def _is_validation_repair(self, summary: OperationReliabilitySummary) -> bool:
        return (
            summary.operation_id in {"qualityFidelity:openCritical", "qualityFidelity:finalGateWarning"}
            or summary.step_key == "validation"
            and summary.operation_id in {"progress", "rankingRevision", "rankingRevision.revisionLoop"}
        )
