"""Owner: upstream.application

Used by: SignalExtractionService to produce complete terminal decision coverage.
Does not own: provider output parsing, grounding, persistence, or project scoring.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from typing import Any

from backend.app.upstream.application.signal_extraction_dossier import SignalExtractionDossier
from backend.app.upstream.domain.signal_extraction_contracts import (
    ExtractedSourceSignal,
    MaterialDecisionRecord,
    MaterialExtractionDecision,
    SignalExtractionOutcome,
)


class SignalExtractionReportBuilder:
    def build(
        self,
        *,
        materials: list[dict[str, Any]],
        dossier: SignalExtractionDossier,
        signals: list[ExtractedSourceSignal],
        provider_decisions: list[MaterialDecisionRecord],
        attempts: list[dict[str, Any]],
        status: str,
        revision: int,
        prior_revisions: list[dict[str, Any]],
        grounding_violations: list[dict[str, Any]] | None = None,
        warnings: list[str] | None = None,
    ) -> SignalExtractionOutcome:
        decisions_by_id = {item.material_id: item for item in provider_decisions}
        signal_ids_by_material: dict[str, list[str]] = {}
        for signal in signals:
            for material_id in dict.fromkeys(ref.material_id for ref in signal.evidence_refs):
                signal_ids_by_material.setdefault(material_id, []).append(signal.id)

        for material in materials:
            material_id = str(material.get("id") or "")
            if material_id in decisions_by_id:
                decision = decisions_by_id[material_id]
                signal_ids = tuple(dict.fromkeys(signal_ids_by_material.get(material_id, [])))
                if signal_ids and decision.decision not in {
                    MaterialExtractionDecision.SIGNAL_PRODUCING,
                    MaterialExtractionDecision.CORROBORATING,
                    MaterialExtractionDecision.CONTRADICTION,
                }:
                    decision = replace(decision, decision=MaterialExtractionDecision.SIGNAL_PRODUCING)
                decisions_by_id[material_id] = replace(decision, signal_ids=signal_ids)
                continue
            if material_id in dossier.language_excluded_material_ids:
                reason = "source-language-not-allowed"
            elif material.get("status") in {"metadataOnly", "skipped", "duplicate"}:
                reason = "material-not-readable"
            elif material_id in dossier.deferred_material_ids:
                reason = "extraction-material-budget"
            elif dossier.readiness == "BLOCKED":
                reason = "no-eligible-evidence-fragments"
            elif "editorial-language-not-satisfied" in (warnings or []):
                reason = "editorial-language-not-satisfied"
            else:
                reason = "provider-did-not-return-decision"
            terminal = (
                MaterialExtractionDecision.EXTRACTION_FAILED
                if status in {"failed", "partial"} and material_id in dossier.eligible_material_ids
                else MaterialExtractionDecision.INSUFFICIENT
            )
            decisions_by_id[material_id] = MaterialDecisionRecord(material_id, terminal, (reason,))

        decisions = [decisions_by_id[str(material.get("id") or "")] for material in materials]
        return SignalExtractionOutcome(
            status=status,
            signals=tuple(signals),
            decisions=tuple(decisions),
            attempts=tuple(attempts),
            grounding_violations=tuple(grounding_violations or []),
            warnings=tuple(warnings or []),
            revision=revision,
            prior_revisions=tuple(prior_revisions),
        )


class SignalExtractionResultPresenter:
    def present(
        self,
        *,
        outcome: SignalExtractionOutcome,
        materials: list[dict[str, Any]],
        dossier: SignalExtractionDossier,
        run: dict[str, Any],
    ) -> dict[str, Any]:
        materials_by_id = {str(item.get("id") or ""): item for item in materials}
        signals = [item.to_payload(materials_by_id) for item in outcome.signals]
        report = outcome.report_payload()
        report.update(
            {
                "runId": run.get("id"),
                "dossier": dossier.trace_payload(),
                "unresolvedEvidenceHandleCount": 0,
                "createdDownstreamArtifacts": {"postCandidates": 0, "planSlots": 0, "draftRuns": 0},
            }
        )
        attempt_ids = [item.get("aiRunId") for item in report["providerAttempts"] if item.get("aiRunId")]
        now = datetime.now(UTC).isoformat()
        operation = {
            "id": f"{run.get('id')}-signal-extraction-r{report['revision']}",
            "runId": run.get("id"),
            "sourceHandleId": str(run.get("radarId") or ""),
            "kind": "signalExtraction",
            "label": "Извлечение доказательных сигналов",
            "status": "succeeded" if outcome.status == "succeeded" else ("skipped" if outcome.status == "notRun" else "failed"),
            "startedAt": now,
            "completedAt": now,
            "foundMaterialIds": list(dossier.eligible_material_ids),
            "aiRunIds": attempt_ids,
        }
        return {"sourceSignals": signals, "signalExtractionReport": report, "operation": operation}


__all__ = ("SignalExtractionReportBuilder", "SignalExtractionResultPresenter")
