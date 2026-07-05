"""Owner: drafting.application.revision

Used by: DraftRun revision package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.validation.draft_validator_orchestrator import DraftValidatorOrchestrator
from backend.app.domain.draft_ranking_revision import RevisionRegressionReport


class DraftRevisionRegressionGuard:
    def __init__(self, validator: DraftValidatorOrchestrator | None = None) -> None:
        self._validator = validator or DraftValidatorOrchestrator()

    def evaluate(
        self,
        *,
        original_candidate_id: str,
        revised_candidate: dict[str, Any] | None,
        validation_report: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
    ) -> RevisionRegressionReport:
        original_counts = _counts_for(validation_report, original_candidate_id)
        if not revised_candidate:
            return RevisionRegressionReport(False, ["revision-not-created"], original_counts, {})
        revised_artifact = {
            "candidates": [revised_candidate],
            "selection": {
                "selectedCandidateId": revised_candidate.get("id"),
                "scorecard": [{"candidateId": revised_candidate.get("id"), "selectionStatus": "eligible", "publishable": True}],
            },
        }
        revised_report = self._validator.validate(
            draft_artifact=revised_artifact,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
        ).to_payload()
        revised_counts = _counts_for(revised_report, str(revised_candidate.get("id") or ""))
        reasons = _regression_reasons(original_counts, revised_counts)
        return RevisionRegressionReport(
            accepted=len(reasons) == 0,
            reasons=reasons or ["revision-preserves-or-improves-deterministic-validation"],
            original_counts=original_counts,
            revised_counts=revised_counts,
            validation_report=revised_report,
        )


def _counts_for(report: dict[str, Any], candidate_id: str) -> dict[str, int]:
    for item in _list(report.get("candidateReports")):
        row = _dict(item)
        if row.get("candidateId") == candidate_id:
            return {
                "critical": _int(row.get("criticalCount")),
                "warning": _int(row.get("warningCount")),
                "missingAttributionClaims": _missing_attribution_count(row),
            }
    return {"critical": 0, "warning": 0, "missingAttributionClaims": 0}


def _regression_reasons(original: dict[str, int], revised: dict[str, int]) -> list[str]:
    reasons: list[str] = []
    if revised.get("critical", 0) > original.get("critical", 0):
        reasons.append("revised-critical-count-increased")
    if revised.get("warning", 0) > original.get("warning", 0):
        reasons.append("revised-warning-count-increased")
    if revised.get("missingAttributionClaims", 0) > original.get("missingAttributionClaims", 0):
        reasons.append("revised-attribution-coverage-regressed")
    return reasons


def _missing_attribution_count(report: dict[str, Any]) -> int:
    missing: set[str] = set()
    for finding in _list(report.get("findings")):
        row = _dict(finding)
        if row.get("validatorId") == "evidence.attribution":
            metadata = _dict(row.get("metadata"))
            missing.update(str(item) for item in _list(metadata.get("missingClaimIds")) if str(item).strip())
    return len(missing)


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _int(value: Any) -> int:
    return int(value) if isinstance(value, (int, float)) else 0
