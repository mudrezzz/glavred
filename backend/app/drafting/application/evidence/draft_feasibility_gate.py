"""Owner: drafting.application.evidence

Used by: DraftRun evidence migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.domain.draft_feasibility import (
    FeasibilityFinding,
    FeasibilityReport,
    FeasibilityStatus,
)
from backend.app.drafting.application.evidence.draft_feasibility_policy import decide_feasibility


class FeasibilityGate:
    def evaluate(self, context_artifact: dict[str, Any]) -> FeasibilityReport:
        brief = _as_dict(context_artifact.get("brief"))
        ledger = _as_dict(context_artifact.get("sourceLedger"))
        claims = _as_list_of_dicts(ledger.get("claims"))
        warnings = _as_list_of_dicts(ledger.get("warnings"))
        risks = _as_list_of_dicts(ledger.get("risks"))
        allowed_ids = _claim_ids(claims, {"canState", "canUseAsFraming"})
        qualified_ids = _claim_ids(claims, {"needsQualification"})
        findings = _findings_from_warnings(warnings)
        findings.extend(_findings_from_risks(risks))
        decision = decide_feasibility(context_artifact, brief, claims, warnings, risks, allowed_ids, qualified_ids)

        return self._report(
            decision.status,
            decision.summary,
            [*findings, *decision.extra_findings],
            allowed_ids,
            qualified_ids,
            decision.blocked,
        )

    def _report(
        self,
        status: FeasibilityStatus,
        summary: str,
        findings: list[FeasibilityFinding],
        allowed_ids: list[str],
        qualified_ids: list[str],
        blocked: bool,
    ) -> FeasibilityReport:
        return FeasibilityReport(
            status=status,
            summary=summary,
            findings=[FeasibilityFinding("status", "info", status.value, summary, "feasibility"), *findings],
            allowed_claim_ids=allowed_ids,
            qualified_claim_ids=qualified_ids,
            blocked=blocked,
            metadata={"version": "feasibility-v1"},
        )


class FeasibilityGatePolicy:
    """Owns migrated helper behavior; module-level aliases remain compatibility-only."""

    @staticmethod
    def _claim_ids(claims: list[dict[str, Any]], allowed_uses: set[str]) -> list[str]:
        return [str(claim.get("id")) for claim in claims if claim.get("id") and claim.get("allowedUse") in allowed_uses]

    @staticmethod
    def _findings_from_warnings(warnings: list[dict[str, Any]]) -> list[FeasibilityFinding]:
        return [
            FeasibilityFinding(
                id=str(item.get("id") or f"warning-{index + 1}"),
                severity="warning",
                title=str(item.get("title") or "Warning"),
                detail=str(item.get("detail") or ""),
                source=str(item.get("source") or "sourceLedger"),
            )
            for index, item in enumerate(warnings)
        ]

    @staticmethod
    def _findings_from_risks(risks: list[dict[str, Any]]) -> list[FeasibilityFinding]:
        return [
            FeasibilityFinding(
                id=str(item.get("id") or f"risk-{index + 1}"),
                severity=str(item.get("severity") or "medium"),
                title=str(item.get("title") or "Risk"),
                detail=str(item.get("detail") or ""),
                source=str(item.get("source") or "sourceLedger"),
            )
            for index, item in enumerate(risks)
        ]

    @staticmethod
    def _as_dict(value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _as_list_of_dicts(value: Any) -> list[dict[str, Any]]:
        return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []

_claim_ids = FeasibilityGatePolicy._claim_ids
_findings_from_warnings = FeasibilityGatePolicy._findings_from_warnings
_findings_from_risks = FeasibilityGatePolicy._findings_from_risks
_as_dict = FeasibilityGatePolicy._as_dict
_as_list_of_dicts = FeasibilityGatePolicy._as_list_of_dicts


__all__ = (
    'FeasibilityGate',
    'FeasibilityGatePolicy',
)
