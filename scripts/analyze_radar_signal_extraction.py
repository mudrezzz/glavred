"""Render structured RadarRun signal-extraction diagnostics from a saved workspace."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import argparse
import json
from typing import Any

from backend.app.infrastructure.sqlite_portfolio_repository import SQLitePortfolioRepository
from backend.app.settings import BackendSettings


class RadarSignalExtractionDiagnostics:
    def analyze(self, *, workspace: dict[str, Any], run_id: str) -> dict[str, Any]:
        run = next((item for item in workspace.get("radarRuns", []) if item.get("id") == run_id), None)
        if not isinstance(run, dict):
            raise ValueError(f"RadarRun not found: {run_id}")
        report = run.get("signalExtraction") if isinstance(run.get("signalExtraction"), dict) else {}
        materials = [
            item for item in workspace.get("foundMaterials", [])
            if item.get("radarRunId") == run_id or item.get("id") in set(run.get("foundMaterialIds") or [])
        ]
        signals = [item for item in workspace.get("sourceSignals", []) if item.get("radarRunId") == run_id]
        decisions = list(report.get("materialDecisions") or [])
        attempts = list(report.get("providerAttempts") or [])
        evidence_refs = [ref for signal in signals for ref in signal.get("evidenceRefs", [])]
        fragment_ids = {
            (str(material.get("id") or ""), str(fragment.get("id") or ""))
            for material in materials
            for fragment in material.get("contentFragments", [])
            if isinstance(fragment, dict)
        }
        unresolved = [
            ref for ref in evidence_refs
            if (str(ref.get("materialId") or ""), str(ref.get("fragmentId") or "")) not in fragment_ids
        ]
        usage = [item.get("providerUsage") for item in attempts if isinstance(item.get("providerUsage"), dict)]
        totals = {
            "inputTokens": sum(int(item.get("prompt_tokens") or item.get("input_tokens") or 0) for item in usage),
            "outputTokens": sum(int(item.get("completion_tokens") or item.get("output_tokens") or 0) for item in usage),
            "totalTokens": sum(int(item.get("total_tokens") or 0) for item in usage),
        }
        downstream = dict(report.get("createdDownstreamArtifacts") or {})
        return {
            "runId": run_id,
            "retrievalStatus": run.get("status"),
            "extractionStatus": report.get("status", "unavailable"),
            "revision": report.get("revision"),
            "retryOutcome": report.get("retryOutcome"),
            "preservedPreviousSignalIds": report.get("preservedPreviousSignalIds") or [],
            "materials": len(materials),
            "materialsWithDecision": len({item.get("materialId") for item in decisions}),
            "decisionCoverageComplete": len(decisions) == len(materials) and len(materials) > 0,
            "decisionCounts": report.get("decisionCounts") or {},
            "signals": len(signals),
            "evidenceRefs": len(evidence_refs),
            "unresolvedEvidenceRefs": unresolved,
            "groundingViolations": report.get("groundingViolations") or [],
            "attempts": attempts,
            "providerUsageTotals": totals,
            "messageCapsRespected": all(
                not (item.get("payloadBudget") or {}).get("incident") and item.get("status") != "blocked"
                for item in attempts
            ),
            "downstreamArtifacts": downstream,
            "downstreamLeakFree": all(int(value or 0) == 0 for value in downstream.values()),
            "warnings": report.get("warnings") or [],
        }

    def markdown(self, report: dict[str, Any]) -> str:
        usage = report["providerUsageTotals"]
        return "\n".join(
            [
                f"# Radar signal extraction: {report['runId']}",
                "",
                "## Статусы",
                f"- Поиск и чтение: `{report['retrievalStatus']}`",
                f"- Извлечение: `{report['extractionStatus']}`, ревизия `{report['revision']}`",
                f"- Результат повтора: `{report['retryOutcome'] or 'не запускался'}`",
                f"- Сохранено сигналов прошлой ревизии: {len(report['preservedPreviousSignalIds'])}",
                "",
                "## Покрытие материалов",
                f"- Материалов: {report['materials']}",
                f"- Терминальных решений: {report['materialsWithDecision']}",
                f"- Полное покрытие: {report['decisionCoverageComplete']}",
                f"- Решения: `{json.dumps(report['decisionCounts'], ensure_ascii=False)}`",
                "",
                "## Сигналы и доказательства",
                f"- Сигналов-кандидатов: {report['signals']}",
                f"- Evidence refs: {report['evidenceRefs']}",
                f"- Неразрешенных refs: {len(report['unresolvedEvidenceRefs'])}",
                f"- Grounding violations: {len(report['groundingViolations'])}",
                "",
                "## Provider и бюджет",
                f"- Попыток: {len(report['attempts'])}",
                f"- Input tokens: {usage['inputTokens']}",
                f"- Output tokens: {usage['outputTokens']}",
                f"- Total tokens: {usage['totalTokens']}",
                f"- Лимиты сообщений соблюдены: {report['messageCapsRespected']}",
                "",
                "## Граница ответственности",
                f"- Downstream artifacts отсутствуют: {report['downstreamLeakFree']}",
                f"- Предупреждения: {', '.join(report['warnings']) or 'нет'}",
            ]
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--db-path", type=Path)
    args = parser.parse_args()
    settings = BackendSettings()
    repository = SQLitePortfolioRepository(args.db_path or settings.portfolio_db_path)
    snapshot = repository.latest_workspace_snapshot(args.project_id)
    if snapshot is None:
        raise SystemExit(f"Workspace snapshot not found: {args.project_id}")
    report = RadarSignalExtractionDiagnostics().analyze(workspace=snapshot.payload, run_id=args.run_id)
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(RadarSignalExtractionDiagnostics().markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
