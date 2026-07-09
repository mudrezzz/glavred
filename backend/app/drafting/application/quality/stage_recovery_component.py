"""Owner: drafting.application.quality

Used by: DraftRun quality/fidelity reporting.
Does not own: final editorial verdicts, evidence coverage policy, provider transport, or persistence.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from typing import Any

from backend.app.shared.llm_operations.incidents import infer_incident_type_value


class QualityFidelityStageRecoveryComponent:
    """Classifies per-operation retry, backup, fallback, and provider incidents."""

    def stage_summaries(self, steps: list[dict[str, Any]], ai_runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        summaries: list[dict[str, Any]] = []
        for step in steps:
            summaries.extend(self._artifact_stage_summaries(str(step.get("key")), _dict(step.get("artifact"))))
        summaries.extend(self._ai_run_summaries(ai_runs, summaries))
        return summaries

    def _artifact_stage_summaries(self, step_key: str, artifact: dict[str, Any]) -> list[dict[str, Any]]:
        summaries: list[dict[str, Any]] = []
        seen: set[str] = set()
        for path, payload in _walk_dicts(artifact):
            envelope = _dict(payload.get("operationEnvelope"))
            attempts = _list(envelope.get("attempts")) or _list(payload.get("attempts"))
            if not envelope and not attempts:
                continue
            operation_id = str(envelope.get("operationId") or payload.get("operationId") or path or step_key)
            dedupe_key = f"{step_key}:{operation_id}"
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            summaries.append(self._summary_from_attempts(step_key, operation_id, attempts, envelope, payload))
        return summaries

    def _summary_from_attempts(
        self,
        step_key: str,
        operation_id: str,
        attempts: list[Any],
        envelope: dict[str, Any],
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        records = [_dict(item) for item in attempts if isinstance(item, dict)]
        accepted = next((item for item in records if _status(item) in {"accepted", "repaired", "backupaccepted", "fallback"}), None)
        incidents = self._incident_types(records, envelope)
        retry_path = self._retry_path(records, envelope, payload)
        return {
            "operationId": operation_id,
            "stepKey": step_key,
            "attemptCount": len(records),
            "acceptedAttemptLabel": accepted.get("label") if accepted else None,
            "provider": _last(records, "provider") or envelope.get("provider"),
            "model": _last(records, "model") or envelope.get("model"),
            "retryPath": retry_path,
            "incidentTypes": incidents,
            "resultImpact": self._result_impact(retry_path, incidents, envelope, payload),
        }

    def _ai_run_summaries(self, ai_runs: list[dict[str, Any]], existing: list[dict[str, Any]]) -> list[dict[str, Any]]:
        existing_ids = {str(summary.get("operationId")) for summary in existing if str(summary.get("operationId") or "").startswith("aiRun:")}
        summaries: list[dict[str, Any]] = []
        for run in ai_runs:
            run_id = str(run.get("id") or "")
            operation_id = f"aiRun:{run_id}"
            if not run_id or operation_id in existing_ids:
                continue
            error = str(run.get("error") or "")
            fallback = bool(run.get("fallbackUsed") or run.get("fallback_used"))
            retry_path = "fallbackRecovered" if fallback else "providerError" if error else "clean"
            summaries.append(
                {
                    "operationId": operation_id,
                    "stepKey": str(run.get("step") or "unknown"),
                    "attemptCount": 1,
                    "acceptedAttemptLabel": None if error and not fallback else "aiRun",
                    "provider": run.get("provider"),
                    "model": run.get("model"),
                    "retryPath": retry_path,
                    "incidentTypes": [_incident_from_error(error)] if error else [],
                    "resultImpact": "fallbackRecovered" if fallback else "providerIncident" if error else "none",
                }
            )
        return summaries

    def _retry_path(self, attempts: list[dict[str, Any]], envelope: dict[str, Any], payload: dict[str, Any]) -> str:
        status = str(envelope.get("status") or payload.get("status") or "").lower()
        if any(bool(item.get("backup")) and _status(item) in {"accepted", "backupaccepted"} for item in attempts) or status == "backupaccepted":
            return "backupRecovered"
        if any(_status(item) == "fallback" for item in attempts) or bool(payload.get("fallbackUsed")) or status == "fallback":
            return "fallbackRecovered"
        accepted_index = next((index for index, item in enumerate(attempts) if _status(item) in {"accepted", "repaired"}), None)
        if accepted_index is not None and accepted_index > 0:
            return "retryRecovered"
        if any(item.get("error") or _status(item) in {"failed", "timeout", "error"} for item in attempts):
            return "providerError"
        return "clean"

    def _result_impact(self, retry_path: str, incidents: list[str], envelope: dict[str, Any], payload: dict[str, Any]) -> str:
        status = str(envelope.get("status") or payload.get("status") or "").lower()
        if status in {"failed", "notrun", "timeout", "cancelled", "stale"}:
            return "stepFailed"
        if retry_path == "providerError":
            return "stepDegraded"
        if retry_path == "fallbackRecovered":
            return "fallbackRecovered"
        if any(item in {"payloadTooLarge", "contextOverBudget"} for item in incidents):
            return "stepDegraded"
        return retry_path if retry_path != "clean" else "none"

    def _incident_types(self, attempts: list[dict[str, Any]], envelope: dict[str, Any]) -> list[str]:
        incidents: list[str] = []
        for item in attempts:
            incident = _dict(item.get("incident"))
            incidents.append(str(incident.get("incidentType") or _incident_from_error(str(item.get("error") or "")) if item.get("error") else ""))
        envelope_incident = _dict(envelope.get("incident"))
        if envelope_incident.get("incidentType"):
            incidents.append(str(envelope_incident["incidentType"]))
        return _unique([item for item in incidents if item])


def _walk_dicts(value: dict[str, Any], path: str = "") -> list[tuple[str, dict[str, Any]]]:
    items = [(path, value)]
    for key, child in value.items():
        if isinstance(child, dict):
            items.extend(_walk_dicts(child, f"{path}.{key}" if path else str(key)))
        elif isinstance(child, list):
            for index, list_child in enumerate(child):
                if isinstance(list_child, dict):
                    items.extend(_walk_dicts(list_child, f"{path}.{key}[{index}]" if path else f"{key}[{index}]"))
    return items


def _incident_from_error(error: str) -> str:
    return infer_incident_type_value(error)


def _status(value: dict[str, Any]) -> str:
    return str(value.get("status") or "").replace("-", "").lower()


def _last(items: list[dict[str, Any]], key: str) -> Any:
    return next((item.get(key) for item in reversed(items) if item.get(key)), None)


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result
