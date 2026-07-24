"""Owner: upstream.application

Used by: SearchOpportunityCoverageReportBuilder.
Does not own: lineage, evidence delivery, provider execution, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from typing import Any


class SearchOpportunityStatusPolicy:
    """Classify useful-yield status without conflating provider and quality failures."""

    def provider_inconclusive(
        self,
        run: dict[str, Any],
        source_signals: list[dict[str, Any]],
    ) -> bool:
        terminal_signals = bool(source_signals) and all(
            str((item.get("utilityReport") or {}).get("recommendation") or "inconclusive")
            != "inconclusive"
            for item in source_signals
        )
        reports = [run.get("signalExtraction"), run.get("signalScoring")]
        if not terminal_signals and any(
            isinstance(report, dict)
            and report.get("status") in {"inconclusive", "notRun"}
            for report in reports
        ):
            return True
        return any(
            isinstance(item, dict)
            and item.get("kind") == "openWebQuery"
            and item.get("status") in {"failed", "skipped"}
            and any(
                marker
                in str(item.get("error") or item.get("skippedReason") or "").lower()
                for marker in ("provider", "openrouter", "timeout", "not-configured")
            )
            for item in run.get("operations", [])
        )

    def first_failure(
        self,
        *,
        executed_query_ids: set[str],
        raw_results: list[dict[str, Any]],
        readable_materials: list[dict[str, Any]],
        signals: list[dict[str, Any]],
        eligible_count: int,
    ) -> str | None:
        if not executed_query_ids:
            return "providerSearch"
        if not raw_results:
            return "triage"
        if not readable_materials:
            return "read"
        if not signals:
            return "signalExtraction"
        if not eligible_count:
            return "signalScoring"
        return None

    def status(
        self,
        *,
        provider_inconclusive: bool,
        eligible_count: int,
        signal_count: int,
        uncovered: tuple[dict[str, Any], ...],
    ) -> str:
        if provider_inconclusive and eligible_count == 0:
            return "inconclusive"
        if eligible_count > 0 and not uncovered:
            return "sufficient"
        if eligible_count > 0 or signal_count > 0:
            return "partial"
        return "zeroYield"

    def reason_codes(
        self,
        *,
        status: str,
        first_failure: str | None,
        provider_inconclusive: bool,
        uncovered: tuple[dict[str, Any], ...],
    ) -> list[str]:
        reasons = [
            f"first-failure-{first_failure}"
            if first_failure
            else "review-eligible-signal-found"
        ]
        if uncovered:
            reasons.append("required-search-requirement-uncovered")
        if provider_inconclusive:
            reasons.append("provider-runtime-inconclusive")
        if status == "zeroYield":
            reasons.append("zero-review-eligible-yield")
        return reasons

    def remediation(
        self,
        stage: str | None,
        provider_inconclusive: bool,
    ) -> list[str]:
        if provider_inconclusive:
            return ["Повторить запуск после восстановления provider/runtime."]
        return {
            "providerSearch": [
                "Проверить provider search и покрытие обязательных запросов."
            ],
            "triage": [
                "Проверить формулировки запросов и причины отклонения результатов."
            ],
            "read": ["Проверить доступность URL и бюджет чтения."],
            "signalExtraction": [
                "Проверить доказательные фрагменты и решения extraction."
            ],
            "signalScoring": [
                "Проверить blocking-критерии и причины utility verdict."
            ],
        }.get(stage, [])


__all__ = ("SearchOpportunityStatusPolicy",)
