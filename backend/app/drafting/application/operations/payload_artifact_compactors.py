"""Owner: drafting.application.operations

Used by: Payload budget compactors for DraftRun artifacts and validation reports.
Does not own: Provider messages, prompt text, or payload budget profiles.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from typing import Any

from backend.app.drafting.application.operations.payload_budget_contracts import PayloadBudgetProfile
from backend.app.drafting.application.operations.payload_compactor_common import CountAccumulator, _drop_empty, _pick, _record, _records
from backend.app.drafting.application.operations.payload_evidence_compactors import EvidenceSynthesisCompactor, PublicEvidenceCompactor, SourceLedgerCompactor
from backend.app.drafting.application.operations.payload_record_compactors import CandidatePayloadCompactor, SummaryRecordCompactor


class ContextArtifactCompactor:
    def __init__(self) -> None:
        self._ledger = SourceLedgerCompactor()
        self._public_evidence = PublicEvidenceCompactor()
        self._synthesis = EvidenceSynthesisCompactor()

    def compact(self, context_artifact: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
        counts: dict[str, int] = {}
        source_ledger, ledger_counts = self._ledger.compact(_record(context_artifact.get("sourceLedger")), profile)
        public_evidence, evidence_counts = self._public_evidence.compact(_record(context_artifact.get("publicEvidence")), profile)
        synthesis, synthesis_counts = self._synthesis.compact(_record(context_artifact.get("evidenceSynthesis")), profile)
        CountAccumulator.merge(counts, ledger_counts)
        CountAccumulator.merge(counts, evidence_counts)
        CountAccumulator.merge(counts, synthesis_counts)
        compact = {
            "contextSummary": _pick(_record(context_artifact.get("contextSummary")), ("brief", "topic", "fabula", "publisher", "publicationSize", "missingContext")),
            "postContract": context_artifact.get("postContract"),
            "sourceLedger": source_ledger,
            "publicEvidence": public_evidence,
            "evidenceSynthesis": synthesis,
            "draftRunBudget": context_artifact.get("draftRunBudget"),
        }
        return _drop_empty(compact), counts


class MaterialPlanCompactor:
    def compact(self, material_plan: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
        counts: dict[str, int] = {}
        compact = _pick(
            material_plan,
            (
                "status",
                "thesis",
                "angle",
                "readerValue",
                "structure",
                "sections",
                "outline",
                "availableEvidence",
                "rejectedEvidence",
                "claimsRequiringAttribution",
                "qualifiedClaims",
                "missingEvidence",
                "riskyClaims",
                "groundingPlan",
                "sourceNotes",
                "openQuestions",
                "warnings",
                "rejectionReasons",
                "evidenceInterpretationSummary",
            ),
        )
        for key in ("usableEvidence", "usableEvidenceCandidates", "evidenceCandidates"):
            if key in material_plan:
                values = _records(material_plan.get(key))
                compact[key] = values[: profile.max_evidence_items]
                CountAccumulator.trimmed(counts, key, len(values), len(compact[key]))
        return _drop_empty(compact), counts


class DraftArtifactCompactor:
    def compact(self, draft_artifact: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
        candidates = _records(draft_artifact.get("candidates"))
        compact = {
            **_pick(draft_artifact, ("status", "scorecard", "selectedCandidateId", "fallbackUsed")),
            "candidates": [CandidatePayloadCompactor.compact(candidate) for candidate in candidates[: profile.max_candidates]],
        }
        counts: dict[str, int] = {}
        CountAccumulator.trimmed(counts, "candidates", len(candidates), len(compact["candidates"]))
        return _drop_empty(compact), counts


class TraceContextCompactor:
    def compact(self, trace_context: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
        compact = _pick(trace_context, ("draftRunId", "traceStatus", "validationSummary", "unresolvedRisks"))
        compact["finalQualityGate"] = SummaryRecordCompactor.compact(_record(trace_context.get("finalQualityGate")))
        compact["alternativeAngleTournament"] = SummaryRecordCompactor.compact(_record(trace_context.get("alternativeAngleTournament")))
        revision_loop = _record(trace_context.get("revisionLoop"))
        prior_drafts = _records(revision_loop.get("cycles"))[: profile.max_prior_drafts]
        compact["revisionLoop"] = _drop_empty(
            {
                "status": revision_loop.get("status"),
                "cycleCount": len(_records(revision_loop.get("cycles"))),
                "cycles": [SummaryRecordCompactor.compact(cycle) for cycle in prior_drafts],
            }
        )
        counts: dict[str, int] = {}
        CountAccumulator.trimmed(counts, "priorDrafts", len(_records(revision_loop.get("cycles"))), len(prior_drafts))
        return _drop_empty(compact), counts


class ValidationReportCompactor:
    def compact(self, report: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
        candidate_reports = _records(report.get("candidateReports"))
        compact = _pick(report, ("status", "summary", "overallStatus", "reason"))
        compact["candidateReports"] = [SummaryRecordCompactor.compact(item) for item in candidate_reports[: profile.max_candidates]]
        counts: dict[str, int] = {}
        CountAccumulator.trimmed(counts, "candidateReports", len(candidate_reports), len(compact["candidateReports"]))
        return _drop_empty(compact), counts
