"""Owner: upstream.application

Used by: explicit RadarRun signal-extraction retry after a prior successful revision.
Does not own: provider calls, workspace persistence, search, reading, or signal scoring.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from typing import Any


class SignalExtractionRetryPolicy:
    def resolve(
        self,
        *,
        existing_report: dict[str, Any] | None,
        existing_signals: list[dict[str, Any]],
        extraction: dict[str, Any],
    ) -> dict[str, Any]:
        if extraction["signalExtractionReport"].get("status") == "succeeded" and existing_signals:
            extraction = self._preserve_stable_signal_ids(
                existing_signals=existing_signals,
                extraction=extraction,
            )
        report = dict(extraction["signalExtractionReport"])
        if report.get("status") == "succeeded" or not existing_signals or not existing_report:
            return extraction
        effective = dict(report)
        for key in (
            "materialDecisions",
            "decisionCounts",
            "decisionCoverageComplete",
            "unresolvedEvidenceHandleCount",
        ):
            if key in existing_report:
                effective[key] = existing_report[key]
        signal_ids = [str(item.get("id") or "") for item in existing_signals if item.get("id")]
        effective.update(
            {
                "status": "partial",
                "retryOutcome": report.get("status"),
                "signalIds": signal_ids,
                "signalCount": len(signal_ids),
                "preservedPreviousSignalIds": signal_ids,
                "warnings": list(dict.fromkeys([*(report.get("warnings") or []), "previous-successful-signals-preserved"])),
            }
        )
        return {**extraction, "sourceSignals": existing_signals, "signalExtractionReport": effective}

    def _preserve_stable_signal_ids(
        self,
        *,
        existing_signals: list[dict[str, Any]],
        extraction: dict[str, Any],
    ) -> dict[str, Any]:
        existing_by_signature = {
            signature: str(signal.get("id") or "")
            for signal in existing_signals
            if (signature := self._evidence_signature(signal)) and signal.get("id")
        }
        remapped_ids: dict[str, str] = {}
        used_existing_ids: set[str] = set()
        signals: list[dict[str, Any]] = []
        for signal in extraction.get("sourceSignals", []):
            current_id = str(signal.get("id") or "")
            stable_id = existing_by_signature.get(self._evidence_signature(signal) or "")
            if stable_id and stable_id not in used_existing_ids:
                remapped_ids[current_id] = stable_id
                used_existing_ids.add(stable_id)
                signals.append({**signal, "id": stable_id})
            else:
                signals.append(signal)

        report = dict(extraction["signalExtractionReport"])
        report["signalIds"] = [remapped_ids.get(str(item or ""), str(item or "")) for item in report.get("signalIds", [])]
        report["materialDecisions"] = [
            {
                **decision,
                "signalIds": [
                    remapped_ids.get(str(item or ""), str(item or ""))
                    for item in decision.get("signalIds", [])
                ],
            }
            for decision in report.get("materialDecisions", [])
        ]
        return {**extraction, "sourceSignals": signals, "signalExtractionReport": report}

    def _evidence_signature(self, signal: dict[str, Any]) -> str | None:
        refs = signal.get("evidenceRefs")
        if not isinstance(refs, list):
            return None
        handles = sorted(
            {
                f"{ref.get('materialId')}:{ref.get('fragmentId')}"
                for ref in refs
                if isinstance(ref, dict) and ref.get("materialId") and ref.get("fragmentId")
            }
        )
        signal_type = str(signal.get("type") or "")
        return f"{signal_type}|{'|'.join(handles)}" if signal_type and handles else None


__all__ = ("SignalExtractionRetryPolicy",)
