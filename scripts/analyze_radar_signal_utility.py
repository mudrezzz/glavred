"""Render structured RadarRun signal-utility and review diagnostics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.infrastructure.sqlite_portfolio_repository import SQLitePortfolioRepository
from backend.app.settings import BackendSettings
from backend.app.upstream.application.signal_utility_profile import ProjectEditorialOpportunityProfileFactory


class RadarSignalUtilityDiagnostics:
    def analyze(self, *, workspace: dict[str, Any], run_id: str) -> dict[str, Any]:
        run = self._find(workspace.get("radarRuns"), run_id)
        if not run:
            raise ValueError(f"RadarRun not found: {run_id}")
        radar = self._find(workspace.get("radars"), str(run.get("radarId") or "")) or {}
        report = run.get("signalScoring") if isinstance(run.get("signalScoring"), dict) else {}
        associated_signals = [
            item for item in workspace.get("sourceSignals", [])
            if isinstance(item, dict) and item.get("radarRunId") == run_id
        ]
        signals = [item for item in associated_signals if item.get("radarId") == run.get("radarId")]
        cross_run_signal_ids = sorted(
            str(item.get("id") or "")
            for item in associated_signals
            if item.get("radarId") != run.get("radarId")
        )
        profile = ProjectEditorialOpportunityProfileFactory().build(
            workspace=workspace,
            radar=radar,
            project_context={
                "projectId": workspace.get("projectId") or "legacy-project",
                "editorialLanguage": run.get("languageContext", {}).get("editorialLanguage") or "ru",
            },
        )
        setting_ids = {item.id for item in profile.settings}
        material_ids, evidence_keys = self._material_evidence_index(workspace, run_id)
        unresolved_settings: list[dict[str, str]] = []
        unresolved_evidence: list[dict[str, str]] = []
        unresolved_relationships: list[dict[str, str]] = []
        recommendations: dict[str, int] = {}
        dimension_count = 0
        radar_criterion_count = 0
        project_criterion_count = 0
        quality_check_count = 0
        relationship_counts: dict[str, int] = {}
        relationship_statuses: dict[str, int] = {}
        signal_summaries: list[dict[str, Any]] = []
        review_events = 0
        signal_ids = {str(item.get("id") or "") for item in signals}
        for signal in signals:
            utility = signal.get("utilityReport") if isinstance(signal.get("utilityReport"), dict) else {}
            recommendation = str(utility.get("recommendation") or "unscored")
            recommendations[recommendation] = recommendations.get(recommendation, 0) + 1
            review_events += len(signal.get("reviewHistory") or [])
            dimensions = utility.get("dimensions") or []
            radar_criteria = utility.get("radarCriteria") or []
            project_criteria = utility.get("projectCriteria") or []
            quality_checks = utility.get("qualityChecks") or []
            dimension_count += len([item for item in dimensions if isinstance(item, dict)])
            radar_criterion_count += len([item for item in radar_criteria if isinstance(item, dict)])
            project_criterion_count += len([item for item in project_criteria if isinstance(item, dict)])
            quality_check_count += len([item for item in quality_checks if isinstance(item, dict)])
            for dimension in [*dimensions, *radar_criteria, *project_criteria]:
                if not isinstance(dimension, dict):
                    continue
                for setting_id in dimension.get("settingRefs") or []:
                    if setting_id not in setting_ids:
                        unresolved_settings.append({"signalId": str(signal.get("id") or ""), "settingId": str(setting_id)})
                for ref in dimension.get("evidenceRefs") or []:
                    self._check_evidence_ref(ref, signal, material_ids, evidence_keys, unresolved_evidence)
            for check in quality_checks:
                if not isinstance(check, dict):
                    continue
                for ref in check.get("evidenceRefs") or []:
                    self._check_evidence_ref(ref, signal, material_ids, evidence_keys, unresolved_evidence)
            relationship = signal.get("relationshipReport") or utility.get("relationshipReport") or {}
            relationship_status = str(relationship.get("status") or "notChecked")
            relationship_statuses[relationship_status] = relationship_statuses.get(relationship_status, 0) + 1
            for item in relationship.get("relations") or []:
                if not isinstance(item, dict):
                    continue
                other_id = str(item.get("otherSignalId") or "")
                kind = str(item.get("kind") or "inconclusive")
                relationship_counts[kind] = relationship_counts.get(kind, 0) + 1
                if other_id not in signal_ids:
                    unresolved_relationships.append({"signalId": str(signal.get("id") or ""), "otherSignalId": other_id})
                for ref in item.get("evidenceRefs") or []:
                    self._check_evidence_ref(ref, signal, material_ids, evidence_keys, unresolved_evidence)
            checks_by_id = {
                str(item.get("checkId") or ""): item
                for item in quality_checks if isinstance(item, dict)
            }
            signal_summaries.append({
                "signalId": str(signal.get("id") or ""),
                "title": str(signal.get("title") or "")[:180],
                "type": str(signal.get("type") or "unknown"),
                "recommendation": recommendation,
                "radarVerdicts": [
                    {"criterionId": item.get("criterionId"), "title": item.get("title"), "verdict": item.get("verdict")}
                    for item in radar_criteria if isinstance(item, dict)
                ],
                "resultSupport": (checks_by_id.get("outcome-support") or {}).get("classification"),
                "sourcePosture": (checks_by_id.get("source-posture") or {}).get("classification"),
                "relationshipStatus": relationship_status,
                "canonicalSignalId": relationship.get("canonicalSignalId"),
            })
        attempts = list(report.get("providerAttempts") or [])
        usage = [item.get("providerUsage") for item in attempts if isinstance(item.get("providerUsage"), dict)]
        usage_totals = {
            "inputTokens": sum(int(item.get("prompt_tokens") or item.get("input_tokens") or 0) for item in usage),
            "outputTokens": sum(int(item.get("completion_tokens") or item.get("output_tokens") or 0) for item in usage),
            "totalTokens": sum(int(item.get("total_tokens") or 0) for item in usage),
        }
        evaluated_ids = {
            str(item.get("signalId") or "")
            for item in report.get("evaluations") or []
            if isinstance(item, dict)
        }
        return {
            "runId": run_id,
            "retrievalStatus": run.get("status"),
            "scoringStatus": report.get("status", "unavailable"),
            "revision": report.get("revision"),
            "signals": len(signals),
            "crossRunSignalIds": cross_run_signal_ids,
            "evaluatedSignals": len(evaluated_ids),
            "unevaluatedSignalIds": sorted(signal_ids - evaluated_ids),
            "recommendations": recommendations,
            "dimensionCount": dimension_count,
            "radarCriterionCount": radar_criterion_count,
            "projectCriterionCount": project_criterion_count,
            "qualityCheckCount": quality_check_count,
            "signalSummaries": signal_summaries,
            "relationshipCounts": relationship_counts,
            "relationshipStatuses": relationship_statuses,
            "unresolvedSettingRefs": unresolved_settings,
            "unresolvedEvidenceRefs": unresolved_evidence,
            "unresolvedRelationshipRefs": unresolved_relationships,
            "providerAttempts": attempts,
            "providerUsageTotals": usage_totals,
            "messageCapsRespected": all(
                item.get("status") != "blocked" and not (item.get("payloadBudget") or {}).get("incident")
                for item in attempts
            ),
            "batchCount": report.get("batchCount", 0),
            "reviewEventCount": review_events,
            "reviewStatuses": self._counts(signals, "reviewStatus"),
            "createdDownstreamArtifacts": report.get("createdDownstreamArtifacts") or {},
        }

    def markdown(self, report: dict[str, Any]) -> str:
        usage = report["providerUsageTotals"]
        return "\n".join([
            f"# Radar signal utility: {report['runId']}",
            "",
            "## Покрытие",
            f"- Статус поиска: `{report['retrievalStatus']}`",
            f"- Статус scoring: `{report['scoringStatus']}`, ревизия `{report['revision']}`",
            f"- Сигналов: {report['signals']}; оценено: {report['evaluatedSignals']}",
            f"- Неоцененные signal ids: {', '.join(report['unevaluatedSignalIds']) or 'нет'}",
            f"- Чужие сигналы с этим run id: {', '.join(report['crossRunSignalIds']) or 'нет'}",
            f"- Рекомендации: `{json.dumps(report['recommendations'], ensure_ascii=False)}`",
            "",
            "## Проверяемость",
            f"- Измерений: {report['dimensionCount']}",
            f"- Критериев радара: {report['radarCriterionCount']}",
            f"- Критериев проекта: {report['projectCriterionCount']}",
            f"- Системных проверок: {report['qualityCheckCount']}",
            f"- Связи: `{json.dumps(report['relationshipCounts'], ensure_ascii=False)}`",
            f"- Статусы проверки связей: `{json.dumps(report['relationshipStatuses'], ensure_ascii=False)}`",
            f"- Неразрешенных setting refs: {len(report['unresolvedSettingRefs'])}",
            f"- Неразрешенных evidence refs: {len(report['unresolvedEvidenceRefs'])}",
            f"- Неразрешенных relationship refs: {len(report['unresolvedRelationshipRefs'])}",
            f"- Review events: {report['reviewEventCount']}",
            f"- Review statuses: `{json.dumps(report['reviewStatuses'], ensure_ascii=False)}`",
            "",
            "## Provider и бюджет",
            f"- Пачек: {report['batchCount']}; попыток: {len(report['providerAttempts'])}",
            f"- Input tokens: {usage['inputTokens']}",
            f"- Output tokens: {usage['outputTokens']}",
            f"- Total tokens: {usage['totalTokens']}",
            f"- Лимиты сообщений соблюдены: {report['messageCapsRespected']}",
            "",
            "## Сигналы",
            *[
                f"- `{item['signalId']}` — {item['title']} | `{item['recommendation']}` | результат `{item['resultSupport']}` | источник `{item['sourcePosture']}` | связи `{item['relationshipStatus']}`"
                for item in report["signalSummaries"]
            ],
        ])

    def _material_evidence_index(
        self, workspace: dict[str, Any], run_id: str
    ) -> tuple[set[str], set[str]]:
        material_ids: set[str] = set()
        evidence_keys: set[str] = set()
        for material in workspace.get("foundMaterials") or []:
            if not isinstance(material, dict) or material.get("radarRunId") != run_id:
                continue
            material_id = str(material.get("id") or "")
            if not material_id:
                continue
            material_ids.add(material_id)
            for fragment in material.get("contentFragments") or []:
                if isinstance(fragment, dict) and fragment.get("id"):
                    evidence_keys.add(f"{material_id}:{fragment['id']}")
        return material_ids, evidence_keys

    def _check_evidence_ref(
        self,
        ref: Any,
        signal: dict[str, Any],
        material_ids: set[str],
        evidence_keys: set[str],
        unresolved: list[dict[str, str]],
    ) -> None:
        if not isinstance(ref, dict):
            return
        material_id = str(ref.get("materialId") or "")
        fragment_id = str(ref.get("fragmentId") or "")
        key = f"{material_id}:{fragment_id}"
        if material_id not in material_ids or key not in evidence_keys:
            unresolved.append({"signalId": str(signal.get("id") or ""), "evidenceKey": key})

    def _find(self, items: Any, item_id: str) -> dict[str, Any] | None:
        if not isinstance(items, list):
            return None
        return next((item for item in items if isinstance(item, dict) and item.get("id") == item_id), None)

    def _counts(self, items: list[dict[str, Any]], field: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in items:
            value = str(item.get(field) or "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts


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
    diagnostics = RadarSignalUtilityDiagnostics()
    report = diagnostics.analyze(workspace=snapshot.payload, run_id=args.run_id)
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.format == "json" else diagnostics.markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
