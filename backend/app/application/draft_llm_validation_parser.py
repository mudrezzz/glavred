from typing import Any

from backend.app.domain.draft_validation import DraftValidatorFinding, DraftValidatorStatus, validation_status_for


def parse_llm_validation_findings(*, candidate_id: str, payload: dict[str, Any]) -> list[DraftValidatorFinding]:
    findings: list[DraftValidatorFinding] = []
    for item in _list(payload.get("findings")):
        raw = _dict(item)
        validator_id = str(raw.get("validatorId") or "llm.editorial-quality")
        if not validator_id.startswith("llm."):
            validator_id = f"llm.{validator_id}"
        findings.append(
            DraftValidatorFinding(
                validator_id=validator_id,
                severity=_severity(raw.get("severity")),
                candidate_id=candidate_id,
                message=str(raw.get("message") or "LLM validator reported an editorial issue."),
                evidence_excerpt=str(raw.get("evidenceExcerpt") or "")[:500],
                repair_guidance=str(raw.get("repairGuidance") or "Review this candidate against the post contract."),
                rule_ids=_strings(raw.get("ruleIds")),
                claim_ids=_strings(raw.get("claimIds")),
                metadata={**_dict(raw.get("metadata")), "llmSummary": str(payload.get("summary") or "")},
            )
        )
    return findings


def status_for_llm_payload(*, candidate_id: str, payload: dict[str, Any]) -> DraftValidatorStatus:
    return validation_status_for(parse_llm_validation_findings(candidate_id=candidate_id, payload=payload))


def _severity(value: Any) -> DraftValidatorStatus:
    normalized = str(value or "").lower()
    if normalized == DraftValidatorStatus.CRITICAL.value:
        return DraftValidatorStatus.CRITICAL
    return DraftValidatorStatus.WARNING


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _strings(value: Any) -> list[str]:
    return [str(item).strip() for item in _list(value) if str(item).strip()]
