from typing import Any


def effective_finding_counts(report: dict[str, Any]) -> dict[str, int]:
    actionable = [_dict(item) for item in _list(report.get("findings")) if is_actionable_finding(_dict(item))]
    return {
        "criticalCount": sum(1 for item in actionable if str(item.get("severity")) == "critical"),
        "warningCount": sum(1 for item in actionable if str(item.get("severity")) == "warning"),
    }


def attribution_finding_split(report: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    actionable: list[dict[str, Any]] = []
    diagnostic: list[dict[str, Any]] = []
    for raw in _list(report.get("findings")):
        finding = _dict(raw)
        validator = str(finding.get("validatorId") or "")
        if not validator.startswith("evidence.attribution"):
            continue
        if is_actionable_finding(finding):
            actionable.append(finding)
        else:
            metadata = _dict(finding.get("metadata"))
            diagnostic.append({
                **finding,
                "metadata": {
                    **metadata,
                    "suppressedReason": metadata.get("suppressedReason") or suppressed_reason(finding),
                },
            })
    return {"actionableAttributionFindings": actionable, "diagnosticAttributionNoise": diagnostic}


def is_actionable_finding(finding: dict[str, Any]) -> bool:
    validator = str(finding.get("validatorId") or "")
    if validator == "evidence.attribution":
        metadata = _dict(finding.get("metadata"))
        expected = _dict(metadata.get("expectedAttributionMarkers"))
        missing = _list(metadata.get("missingClaimIds"))
        return any(_list(expected.get(str(claim_id))) for claim_id in missing)
    if validator.startswith("evidence.attribution"):
        return False
    return str(finding.get("severity") or "") in {"warning", "critical"}


def suppressed_reason(finding: dict[str, Any]) -> str:
    metadata = _dict(finding.get("metadata"))
    if metadata.get("suppressedReason"):
        return str(metadata["suppressedReason"])
    if str(finding.get("validatorId") or "") == "evidence.attribution":
        return "empty-attribution-markers"
    return "diagnostic-attribution-finding"


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
