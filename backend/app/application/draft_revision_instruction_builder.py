from typing import Any

from backend.app.domain.draft_ranking_revision import DirectedRevisionInstruction

ACTIONABLE_VALIDATORS = (
    "evidence.attribution",
    "evidence.rejected-proof",
    "size.",
    "shape.",
    "contract.",
    "rules.",
    "publishability.",
    "llm.source-grounding",
)


class DraftRevisionInstructionBuilder:
    def build(self, *, candidate_id: str | None, validation_report: dict[str, Any]) -> DirectedRevisionInstruction:
        if not candidate_id:
            return DirectedRevisionInstruction(candidate_id=None, status="not-created", reason="no-ranked-candidate")
        findings = _candidate_findings(validation_report, candidate_id)
        actionable = [finding for finding in findings if _is_actionable(finding)]
        if not actionable:
            return DirectedRevisionInstruction(candidate_id=candidate_id, status="not-run", reason="no-actionable-findings")
        return DirectedRevisionInstruction(
            candidate_id=candidate_id,
            status="created",
            repair_goals=[_repair_goal(finding) for finding in actionable[:8]],
            source_findings=actionable[:8],
        )


def _candidate_findings(validation_report: dict[str, Any], candidate_id: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for report in _list(validation_report.get("candidateReports")):
        row = _dict(report)
        if row.get("candidateId") == candidate_id:
            findings.extend(_dict(item) for item in _list(row.get("findings")))
    llm_report = _dict(validation_report.get("llmValidationReport"))
    for report in _list(llm_report.get("candidateReports")):
        row = _dict(report)
        if row.get("candidateId") == candidate_id:
            findings.extend(_dict(item) for item in _list(row.get("findings")))
    return findings


def _is_actionable(finding: dict[str, Any]) -> bool:
    validator_id = str(finding.get("validatorId") or "")
    severity = str(finding.get("severity") or "")
    guidance = str(finding.get("repairGuidance") or "")
    return severity in {"warning", "critical"} and guidance and any(validator_id.startswith(prefix) for prefix in ACTIONABLE_VALIDATORS)


def _repair_goal(finding: dict[str, Any]) -> str:
    validator_id = str(finding.get("validatorId") or "validator")
    message = str(finding.get("message") or "")
    guidance = str(finding.get("repairGuidance") or "")
    return f"{validator_id}: {message} Repair: {guidance}".strip()


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
