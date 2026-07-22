"""Owner: upstream.application

Used by: SignalUtilityScoringService to serialize trace-safe scoring results.
Does not own: provider calls, recommendation decisions, review lifecycle, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from backend.app.upstream.domain.signal_utility import SignalUtilityDossier, SignalUtilityEvaluation


class SignalUtilityReportBuilder:
    def build(
        self,
        *,
        run_id: str,
        signals: list[dict[str, Any]],
        evaluations: list[SignalUtilityEvaluation],
        dossiers: list[SignalUtilityDossier],
        attempts: list[dict[str, Any]],
        revision: int,
        previous_report: dict[str, Any] | None,
    ) -> dict[str, Any]:
        by_id = {item.signal_id: item for item in evaluations}
        updated_signals: list[dict[str, Any]] = []
        report_evaluations: list[dict[str, Any]] = []
        for signal in signals:
            signal_id = str(signal.get("id") or "")
            evaluation = by_id[signal_id]
            utility = evaluation.to_payload(revision=revision)
            report_evaluations.append({"signalId": signal_id, **utility})
            updated_signals.append(
                {
                    **signal,
                    "utilityReport": utility,
                    "relationshipReport": utility.get("relationshipReport"),
                    "utilityRevision": revision,
                    "legacyIntegrityStatus": "current",
                    "filterStatus": self._legacy_status(evaluation.recommendation.value),
                    "filterEvaluations": [],
                }
            )
        prior = list((previous_report or {}).get("revisions") or [])
        if previous_report and (not prior or prior[-1].get("revision") != previous_report.get("revision")):
            prior.append({"revision": previous_report.get("revision"), "status": previous_report.get("status")})
        status = (
            "notRun"
            if not evaluations
            else "succeeded"
            if all(item.recommendation.value != "inconclusive" for item in evaluations)
            else "inconclusive"
        )
        dossier_traces = [item.trace_payload() for item in dossiers]
        report = {
            "version": 2,
            "runId": run_id,
            "status": status,
            "revision": revision,
            "revisions": [*prior, {"revision": revision, "status": status}],
            "signalIds": [str(item.get("id") or "") for item in signals],
            "evaluations": report_evaluations,
            "providerAttempts": attempts,
            "dossier": dossier_traces[0] if len(dossier_traces) == 1 else None,
            "dossiers": dossier_traces,
            "batchCount": len([item for item in dossiers if item.signal_ids]),
            "unresolvedSettingRefCount": 0,
            "unresolvedEvidenceRefCount": 0,
            "decisionCoverageComplete": len(evaluations) == len(signals),
            "createdDownstreamArtifacts": {"postCandidates": 0, "planSlots": 0, "draftRuns": 0},
        }
        now = datetime.now(UTC).isoformat()
        operation = {
            "id": f"{run_id}-signal-scoring-r{revision}",
            "runId": run_id,
            "sourceHandleId": "signal-utility",
            "kind": "signalScoring",
            "label": "Оценка редакционной полезности сигналов",
            "status": "succeeded" if status == "succeeded" else "skipped" if status == "notRun" else "failed",
            "startedAt": now,
            "completedAt": now,
            "aiRunIds": [item.get("aiRunId") for item in attempts if item.get("aiRunId")],
        }
        return {"sourceSignals": updated_signals, "signalScoringReport": report, "operation": operation}

    def _legacy_status(self, recommendation: str) -> str | None:
        return {
            "recommended": "passed",
            "reviewWithCaution": "warning",
            "notRecommended": "rejected",
        }.get(recommendation)


__all__ = ("SignalUtilityReportBuilder",)
