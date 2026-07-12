"""Owner: drafting.application.quality

Used by: DraftRun quality/fidelity reporting.
Does not own: validation rule execution, final-gate assessment, provider recovery, or persistence.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from hashlib import sha256
from typing import Any

from backend.app.drafting.application.quality.issue_scope_policy import QualityIssueScopePolicy


class QualityFidelityIssueComponent:
    """Classifies findings and limits blocking counts to the delivered candidate."""

    def __init__(self, scope_policy: QualityIssueScopePolicy | None = None) -> None:
        self._scope_policy = scope_policy or QualityIssueScopePolicy()

    def summary(self, steps: list[dict[str, Any]]) -> dict[str, Any]:
        final_candidate_id = self._final_candidate_id(steps)
        lifecycle = [
            self._finding_lifecycle(item, final_candidate_id)
            for item in self._findings(steps, final_candidate_id)
        ]
        return {
            "finalCandidateId": final_candidate_id,
            "criticalCount": self._count(lifecycle, severity="critical"),
            "warningCount": self._count(lifecycle, severity="warning"),
            "openCriticalCount": self._count(lifecycle, severity="critical", status="open"),
            "openWarningCount": self._count(lifecycle, severity="warning", status="open"),
            "diagnosticCriticalCount": self._count(lifecycle, severity="critical", scope="nonFinalCandidate"),
            "diagnosticWarningCount": self._count(lifecycle, severity="warning", scope="nonFinalCandidate"),
            "finalGateCriticalCount": self._final_gate_count(lifecycle, "critical"),
            "finalGateWarningCount": self._final_gate_count(lifecycle, "warning"),
            "resolvedCount": self._count(lifecycle, status="resolved"),
            "suppressedCount": self._count(lifecycle, status="suppressed"),
            "acceptedRiskCount": self._count(lifecycle, status="acceptedRisk"),
            "items": lifecycle,
        }

    def final_gate(self, steps: list[dict[str, Any]]) -> dict[str, Any]:
        original = self._raw_final_gate(steps)
        repaired = _dict(original.get("repairGate"))
        if original.get("acceptedRepair") and repaired:
            return {
                **repaired,
                "acceptedRepair": True,
                "initialStatus": original.get("status"),
                "finalDecision": original.get("finalDecision"),
                "effectiveGateSource": "acceptedRepair",
            }
        return {**original, "effectiveGateSource": "initial"} if original else {}

    def _findings(self, steps: list[dict[str, Any]], final_candidate_id: str | None) -> list[dict[str, Any]]:
        validation = _artifact(steps, "validation")
        findings: list[dict[str, Any]] = []
        findings.extend(self._candidate_findings(validation.get("candidateReports"), "deterministicValidation"))
        llm = _dict(validation.get("llmValidationReport"))
        findings.extend(self._candidate_findings(llm.get("candidateReports"), "llmValidation"))

        original_gate = self._raw_final_gate(steps)
        effective_gate = self.final_gate(steps)
        if original_gate.get("acceptedRepair"):
            findings.extend(self._gate_findings(original_gate, final_candidate_id, resolved_reason="accepted-final-repair"))
            self._append_gate_status(findings, original_gate, final_candidate_id, resolved_reason="accepted-final-repair", source="finalQualityGateInitial")
        findings.extend(self._gate_findings(effective_gate, final_candidate_id))
        self._append_gate_status(findings, effective_gate, final_candidate_id)
        return self._dedupe(findings)

    def _candidate_findings(self, reports_value: Any, source: str) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        for report in _list(reports_value):
            row = _dict(report)
            candidate_id = _optional_string(row.get("candidateId"))
            for item in _list(row.get("findings")):
                finding = {**_dict(item), "source": source}
                if candidate_id and not finding.get("candidateId"):
                    finding["candidateId"] = candidate_id
                findings.append(finding)
        return findings

    def _gate_findings(
        self,
        gate: dict[str, Any],
        final_candidate_id: str | None,
        *,
        resolved_reason: str | None = None,
    ) -> list[dict[str, Any]]:
        independent = _dict(gate.get("independentReview"))
        candidate_id = _optional_string(independent.get("candidateId") or gate.get("candidateId") or final_candidate_id)
        return [
            {
                **_dict(item),
                "candidateId": _dict(item).get("candidateId") or candidate_id,
                "source": "finalQualityGate",
                **({"resolvedReason": resolved_reason} if resolved_reason else {}),
            }
            for item in _list(independent.get("findings"))
        ]

    def _append_gate_status(
        self,
        findings: list[dict[str, Any]],
        gate: dict[str, Any],
        final_candidate_id: str | None,
        *,
        resolved_reason: str | None = None,
        source: str = "finalQualityGate",
    ) -> None:
        status = str(gate.get("status") or "")
        if status not in {"warning", "critical"}:
            return
        independent = _dict(gate.get("independentReview"))
        if any(str(_dict(item).get("severity") or "") in {"warning", "critical"} for item in _list(independent.get("findings"))):
            return
        final_decision = _dict(gate.get("finalDecision"))
        findings.append(
            {
                "validatorId": "finalQualityGate.status",
                "severity": status,
                "candidateId": independent.get("candidateId") or gate.get("candidateId") or final_candidate_id,
                "message": str(gate.get("summary") or final_decision.get("reason") or status),
                "source": source,
                "metadata": self._final_gate_metadata(gate),
                **({"resolvedReason": resolved_reason} if resolved_reason else {}),
            }
        )

    def _finding_lifecycle(self, finding: dict[str, Any], final_candidate_id: str | None) -> dict[str, Any]:
        severity = str(finding.get("severity") or finding.get("status") or "warning")
        severity = severity if severity in {"critical", "warning"} else "warning"
        candidate_id = _optional_string(finding.get("candidateId") or _dict(finding.get("metadata")).get("candidateId"))
        scope = self._scope_policy.classify(candidate_id=candidate_id, final_candidate_id=final_candidate_id)
        status, reason = self._status(finding, scope.resolved_reason)
        source = str(finding.get("source") or "validation")
        validator_id = str(finding.get("validatorId") or finding.get("id") or "unknown")
        message = str(finding.get("message") or "")[:180]
        return {
            "id": self._stable_id(source, candidate_id, validator_id, message),
            "candidateId": candidate_id,
            "validatorId": validator_id,
            "severity": severity,
            "status": status,
            "scope": scope.scope,
            "appliesToFinalDraft": scope.applies_to_final_draft,
            "message": message,
            "source": source,
            "statusReason": reason,
        }

    def _status(self, finding: dict[str, Any], scope_reason: str | None) -> tuple[str, str]:
        metadata = _dict(finding.get("metadata"))
        suppressed = finding.get("suppressedReason") or metadata.get("suppressedReason")
        if suppressed:
            return "suppressed", str(suppressed)
        accepted_risk = finding.get("acceptedRiskReason") or metadata.get("acceptedRiskReason")
        if finding.get("acceptedRisk") or metadata.get("acceptedRisk") or accepted_risk:
            return "acceptedRisk", str(accepted_risk or "accepted-risk")
        resolved = finding.get("resolvedReason") or metadata.get("resolvedReason") or scope_reason
        if resolved:
            return "resolved", str(resolved)
        return "open", "unresolved"

    def _final_candidate_id(self, steps: list[dict[str, Any]]) -> str | None:
        validation = _artifact(steps, "validation")
        ranking = _dict(validation.get("rankingRevision"))
        decision = _dict(ranking.get("finalDecision"))
        gate_decision = _dict(_dict(ranking.get("finalQualityGate")).get("finalDecision"))
        return _optional_string(decision.get("finalCandidateId") or gate_decision.get("finalCandidateId"))

    def _raw_final_gate(self, steps: list[dict[str, Any]]) -> dict[str, Any]:
        validation = _artifact(steps, "validation")
        return _dict(_dict(validation.get("rankingRevision")).get("finalQualityGate"))

    def _final_gate_metadata(self, final_gate: dict[str, Any]) -> dict[str, Any]:
        repair = _dict(final_gate.get("repair"))
        final_decision = _dict(final_gate.get("finalDecision"))
        return {
            "acceptedRepair": bool(final_gate.get("acceptedRepair")),
            "repairStatus": repair.get("status"),
            "repairDecisionStatus": repair.get("decisionStatus"),
            "finalDecisionSource": final_decision.get("source"),
            "finalDecisionReason": final_decision.get("reason"),
            "acceptedRisk": final_gate.get("acceptedRisk"),
            "acceptedRiskReason": final_gate.get("acceptedRiskReason"),
            "suppressedReason": final_gate.get("suppressedReason"),
        }

    def _dedupe(self, findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        seen: set[tuple[str, str, str, str]] = set()
        for finding in findings:
            identity = (
                str(finding.get("source") or "validation"),
                str(finding.get("candidateId") or "unknown"),
                str(finding.get("validatorId") or finding.get("id") or "unknown"),
                " ".join(str(finding.get("message") or "").lower().split()),
            )
            if identity not in seen:
                seen.add(identity)
                result.append(finding)
        return result

    def _stable_id(self, source: str, candidate_id: str | None, validator_id: str, message: str) -> str:
        identity = "|".join((source, candidate_id or "unknown", validator_id, " ".join(message.lower().split())))
        return f"quality-issue:{sha256(identity.encode('utf-8')).hexdigest()[:16]}"

    def _count(self, items: list[dict[str, Any]], **filters: str) -> int:
        return sum(1 for item in items if all(item.get(key) == value for key, value in filters.items()))

    def _final_gate_count(self, items: list[dict[str, Any]], severity: str) -> int:
        return sum(1 for item in items if item.get("severity") == severity and str(item.get("source") or "").startswith("finalQualityGate"))


def _artifact(steps: list[dict[str, Any]], key: str) -> dict[str, Any]:
    return next((_dict(step.get("artifact")) for step in steps if step.get("key") == key), {})


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _optional_string(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None
