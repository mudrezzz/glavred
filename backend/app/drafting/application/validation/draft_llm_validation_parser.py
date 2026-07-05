"""Owner: drafting.application.validation

Used by: DraftRun validation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.validation.draft_llm_validation_observations import (
    is_llm_observation_like,
    llm_observation,
    normalize_llm_validator_id,
)
from backend.app.domain.draft_llm_validation import LlmValidatorObservation
from backend.app.domain.draft_validation import DraftValidatorFinding, DraftValidatorStatus, validation_status_for


def parse_llm_validation_report(
    *,
    candidate_id: str,
    payload: dict[str, Any],
) -> tuple[list[DraftValidatorFinding], list[LlmValidatorObservation]]:
    findings: list[DraftValidatorFinding] = []
    observations: list[LlmValidatorObservation] = []
    for item in _list(payload.get("findings")):
        raw = _dict(item)
        if is_llm_observation_like(raw):
            observations.append(llm_observation(candidate_id=candidate_id, payload=payload, raw=raw))
        else:
            findings.append(_finding(candidate_id=candidate_id, payload=payload, raw=raw))
    for item in _list(payload.get("observations")):
        observations.append(llm_observation(candidate_id=candidate_id, payload=payload, raw=_dict(item)))
    return findings, observations


def parse_llm_validation_findings(*, candidate_id: str, payload: dict[str, Any]) -> list[DraftValidatorFinding]:
    return parse_llm_validation_report(candidate_id=candidate_id, payload=payload)[0]


def status_for_llm_payload(*, candidate_id: str, payload: dict[str, Any]) -> DraftValidatorStatus:
    return validation_status_for(parse_llm_validation_findings(candidate_id=candidate_id, payload=payload))


def _severity(value: Any) -> DraftValidatorStatus:
    normalized = str(value or "").lower()
    if normalized == DraftValidatorStatus.CRITICAL.value:
        return DraftValidatorStatus.CRITICAL
    return DraftValidatorStatus.WARNING


def _finding(*, candidate_id: str, payload: dict[str, Any], raw: dict[str, Any]) -> DraftValidatorFinding:
    return DraftValidatorFinding(
        validator_id=normalize_llm_validator_id(raw),
        severity=_severity(raw.get("severity")),
        candidate_id=candidate_id,
        message=str(raw.get("message") or "LLM validator reported an editorial issue."),
        evidence_excerpt=str(raw.get("evidenceExcerpt") or "")[:500],
        repair_guidance=str(raw.get("repairGuidance") or "Review this candidate against the post contract."),
        rule_ids=_strings(raw.get("ruleIds")),
        claim_ids=_strings(raw.get("claimIds")),
        metadata={**_dict(raw.get("metadata")), "llmSummary": str(payload.get("summary") or "")},
    )


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _strings(value: Any) -> list[str]:
    return [str(item).strip() for item in _list(value) if str(item).strip()]
