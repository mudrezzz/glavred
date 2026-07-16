"""Owner: upstream.application.benchmark

Used by: deterministic regression tests for evidence-backed signal extraction.
Does not own: live provider execution, retrieval scoring, project utility, or candidate assembly.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.app.upstream.application.provider_budget_profiles import UpstreamProviderBudgetProfileRegistry
from backend.app.upstream.application.signal_extraction_context import SignalExtractionDossierFactory
from backend.app.upstream.application.signal_extraction_fragments import FoundMaterialFragmentPolicy
from backend.app.upstream.application.signal_extraction_validation import SignalExtractionPayloadMapper


class RecordedSignalExtractionBenchmark:
    def __init__(self, fixture_path: Path | None = None) -> None:
        self._fixture_path = fixture_path or Path(__file__).with_name("fixtures") / "benchmark-signal-extraction-industrial-ai.json"
        self._fragments = FoundMaterialFragmentPolicy()
        self._dossiers = SignalExtractionDossierFactory()
        self._mapper = SignalExtractionPayloadMapper()

    def run(self) -> dict[str, Any]:
        fixture = json.loads(self._fixture_path.read_text(encoding="utf-8"))
        failures: list[dict[str, Any]] = []
        case_reports: list[dict[str, Any]] = []
        profile = UpstreamProviderBudgetProfileRegistry().resolve(operation_id="signalExtraction", execution_mode="standard")
        for case in fixture["cases"]:
            source = case["material"]
            fragments = self._fragments.from_read_text(material_id=source["id"], text=source["text"])
            material = {
                **source,
                "radarRunId": "recorded-run",
                "sourceHandleId": "recorded-source",
                "locator": f"https://recorded.example/{source['id']}",
                "summary": source["text"],
                "status": "found",
                "capturedAt": "2026-07-14T00:00:00+00:00",
                "provenanceLabel": "recorded",
                "contentFragments": fragments,
            }
            dossier = self._dossiers.build(context={"radarId": "recorded-radar"}, materials=[material], profile=profile)
            payload_text = json.dumps(case["payload"], ensure_ascii=False)
            payload_text = payload_text.replace("$fragment", fragments[0]["id"]).replace("$text", fragments[0]["text"])
            payload = json.loads(payload_text)
            try:
                signals, decisions, violations = self._mapper.map(
                    payload=payload,
                    dossier=dossier,
                    radar_id="recorded-radar",
                    run_id="recorded-run",
                )
                actual = decisions[0].decision.value
                passed = actual == case["expectedDecision"] and not violations
            except Exception as exc:
                signals, decisions, violations = [], [], []
                actual = "error"
                passed = False
                failures.append({"caseId": case["id"], "error": f"{exc.__class__.__name__}:{str(exc)}"})
            if not passed and actual != "error":
                failures.append({"caseId": case["id"], "expected": case["expectedDecision"], "actual": actual})
            case_reports.append(
                {"caseId": case["id"], "passed": passed, "decision": actual, "signalCount": len(signals)}
            )
        return {
            "scenarioId": fixture["id"],
            "status": "passed" if not failures else "failed",
            "caseCount": len(case_reports),
            "passedCount": sum(1 for item in case_reports if item["passed"]),
            "failures": failures,
            "cases": case_reports,
        }


def run_signal_extraction_golden_benchmark() -> dict[str, Any]:
    return RecordedSignalExtractionBenchmark().run()


__all__ = ("RecordedSignalExtractionBenchmark", "run_signal_extraction_golden_benchmark")
