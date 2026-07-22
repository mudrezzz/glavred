"""Owner: upstream.application

Used by: workspace-facing signal APIs to classify legacy signal contracts without provider calls.
Does not own: re-extraction, scoring, review transitions, or UI grouping.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from typing import Any


class LegacySignalIntegrityPolicy:
    def normalize(self, signal: dict[str, Any]) -> dict[str, Any]:
        if signal.get("editorialLanguage") and isinstance(signal.get("utilityReport"), dict):
            return {**signal, "legacyIntegrityStatus": signal.get("legacyIntegrityStatus") or "current"}
        legacy_evaluation = None
        if signal.get("filterStatus") or signal.get("filterEvaluations"):
            legacy_evaluation = {
                "status": signal.get("filterStatus"),
                "evaluations": list(signal.get("filterEvaluations") or []),
                "source": "legacy-client-keyword-evaluator",
                "canonical": False,
            }
        normalized = {
            **signal,
            "legacyIntegrityStatus": "needsReExtraction",
            "legacyUtilityEvaluation": legacy_evaluation,
        }
        normalized.pop("filterStatus", None)
        normalized.pop("filterEvaluations", None)
        return normalized

    def normalize_workspace(self, workspace: dict[str, Any]) -> dict[str, Any]:
        return {
            **workspace,
            "sourceSignals": [
                self.normalize(item) for item in workspace.get("sourceSignals", []) if isinstance(item, dict)
            ],
        }


__all__ = ("LegacySignalIntegrityPolicy",)
