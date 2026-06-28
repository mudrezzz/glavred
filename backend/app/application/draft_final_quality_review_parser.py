from typing import Any


VALID_STATUSES = {"passed", "warning", "critical"}


def normalize_final_quality_review(payload: dict[str, Any], *, candidate_id: str) -> dict[str, Any]:
    findings = [_finding(item, index, candidate_id) for index, item in enumerate(_list(payload.get("findings")), start=1)]
    findings = [item for item in findings if item]
    observations = [_observation(item) for item in _list(payload.get("observations"))]
    status = _status(payload.get("status") or _status_from_findings(findings))
    return {
        "status": status,
        "summary": str(payload.get("summary") or ""),
        "candidateId": candidate_id,
        "publicProseStatus": _status(payload.get("publicProseStatus") or status),
        "sourceIntegrationStatus": _status(payload.get("sourceIntegrationStatus") or status),
        "authorVoiceStrength": _status(payload.get("authorVoiceStrength") or "passed"),
        "readerValueClarity": _status(payload.get("readerValueClarity") or "passed"),
        "findings": findings,
        "observations": observations,
        "repairGoals": _strings(payload.get("repairGoals"))[:8],
    }


def _finding(value: Any, index: int, candidate_id: str) -> dict[str, Any] | None:
    row = _dict(value)
    severity = _status(row.get("severity") or row.get("status") or "warning")
    guidance = str(row.get("repairGuidance") or "").strip()
    message = str(row.get("message") or row.get("summary") or "").strip()
    if severity == "passed" or not (message or guidance):
        return None
    return {
        "id": str(row.get("id") or f"final-quality-{index}"),
        "validatorId": "finalQuality.independentReview",
        "severity": severity,
        "candidateId": candidate_id,
        "message": message or guidance,
        "evidenceExcerpt": str(row.get("evidenceExcerpt") or "")[:500],
        "repairGuidance": guidance,
        "metadata": {
            "contractCriterion": str(row.get("contractCriterion") or ""),
        },
    }


def _observation(value: Any) -> dict[str, str]:
    row = _dict(value)
    return {"message": str(row.get("message") or row.get("summary") or value or "")}


def _status(value: Any) -> str:
    text = str(value or "passed").strip().lower()
    return text if text in VALID_STATUSES else "warning"


def _status_from_findings(findings: list[dict[str, Any]]) -> str:
    if any(item.get("severity") == "critical" for item in findings):
        return "critical"
    if findings:
        return "warning"
    return "passed"


def _strings(value: Any) -> list[str]:
    return [str(item).strip() for item in value if str(item).strip()] if isinstance(value, list) else []


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
