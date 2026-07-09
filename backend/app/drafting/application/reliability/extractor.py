"""Owner: drafting.application.reliability

Used by: DraftRun provider reliability analytics.
Does not own: quality/fidelity verdict policy, provider calls, DraftRun persistence, or CLI parsing.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from typing import Any

from backend.app.domain.ai_run import AiRun
from backend.app.domain.draft_run import DraftRun
from backend.app.drafting.application.quality import DraftRunQualityFidelityReporter
from backend.app.drafting.application.reliability.ai_run_event_component import (
    ChildAiRunReliabilityEventComponent,
)
from backend.app.drafting.application.reliability.contracts import OperationReliabilityEvent
from backend.app.drafting.application.reliability.quality_signal_extractor import (
    QualityFidelityReliabilitySignalExtractor,
)
from backend.app.drafting.application.reliability.raw_artifact_event_component import (
    RawArtifactReliabilityEventComponent,
)
from backend.app.drafting.application.reliability.stage_incident_refinement import (
    LegacyStageIncidentRefinementComponent,
)


class DraftRunReliabilityExtractor:
    """Extracts structured reliability events without parsing diagnostic prose."""

    def __init__(
        self,
        quality_reporter: DraftRunQualityFidelityReporter | None = None,
        quality_signals: QualityFidelityReliabilitySignalExtractor | None = None,
        ai_run_events: ChildAiRunReliabilityEventComponent | None = None,
        raw_artifact_events: RawArtifactReliabilityEventComponent | None = None,
        stage_incident_refinement: LegacyStageIncidentRefinementComponent | None = None,
    ) -> None:
        self._quality_reporter = quality_reporter or DraftRunQualityFidelityReporter()
        self._quality_signals = quality_signals or QualityFidelityReliabilitySignalExtractor()
        self._ai_run_events = ai_run_events or ChildAiRunReliabilityEventComponent()
        self._raw_artifact_events = raw_artifact_events or RawArtifactReliabilityEventComponent()
        self._stage_incident_refinement = stage_incident_refinement or LegacyStageIncidentRefinementComponent()

    def from_draft_run(self, run: DraftRun, ai_runs: list[AiRun] | None = None) -> list[OperationReliabilityEvent]:
        ai_payloads = [self._ai_run_payload(item) for item in ai_runs or []]
        steps = [
            {
                "key": step.key.value,
                "status": step.status.value,
                "artifact": step.artifact_payload or {},
            }
            for step in run.steps
        ]
        quality = self._quality_report(steps, run.final_draft, run.status.value, ai_payloads)
        execution_mode = self._execution_mode(run.request_payload, steps)
        events = self.from_quality_fidelity(
            run_id=run.id,
            quality_fidelity=quality,
            execution_mode=execution_mode,
        )
        events = self._stage_incident_refinement.refine(events, ai_payloads)
        events.extend(
            self._ai_run_events.missing_events(
                run_id=run.id,
                ai_runs=ai_payloads,
                existing=events,
                execution_mode=execution_mode,
            )
        )
        events.extend(
            self._raw_artifact_events.events(
                run_id=run.id,
                steps=steps,
                existing=events,
                execution_mode=execution_mode,
            )
        )
        return events

    def from_quality_fidelity(
        self,
        *,
        run_id: str,
        quality_fidelity: dict[str, Any],
        execution_mode: str | None = None,
    ) -> list[OperationReliabilityEvent]:
        events = [
            self._stage_event(run_id, stage, execution_mode)
            for stage in _list(quality_fidelity.get("stageSummaries"))
            if isinstance(stage, dict)
        ]
        events.extend(
            self._quality_signals.events(
                run_id=run_id,
                quality_fidelity=quality_fidelity,
                execution_mode=execution_mode,
            )
        )
        return events

    def _quality_report(
        self,
        steps: list[dict[str, Any]],
        final_draft: dict[str, Any] | None,
        run_status: str,
        ai_runs: list[dict[str, Any]],
    ) -> dict[str, Any]:
        embedded = self._embedded_quality_report(steps)
        if embedded:
            return embedded
        return self._quality_reporter.build(
            run_status=run_status,
            steps=steps,
            final_draft=final_draft,
            ai_runs=ai_runs,
        )

    def _embedded_quality_report(self, steps: list[dict[str, Any]]) -> dict[str, Any]:
        for step in reversed(steps):
            artifact = _dict(step.get("artifact"))
            if isinstance(artifact.get("qualityFidelity"), dict):
                return artifact["qualityFidelity"]
            ranking = _dict(_dict(artifact.get("rankingRevision")).get("qualityFidelity"))
            if ranking:
                return ranking
        return {}

    def _stage_event(
        self,
        run_id: str,
        stage: dict[str, Any],
        execution_mode: str | None,
    ) -> OperationReliabilityEvent:
        incident_types = _canonical_incident_types(stage.get("incidentTypes"))
        return OperationReliabilityEvent(
            run_id=run_id,
            step_key=str(stage.get("stepKey") or "unknown"),
            operation_id=str(stage.get("operationId") or "unknown"),
            operation_kind=self._operation_kind(str(stage.get("operationId") or "")),
            provider=_optional_str(stage.get("provider")),
            model=_optional_str(stage.get("model")),
            model_role=_optional_str(stage.get("modelRole")),
            execution_mode=execution_mode,
            attempt_count=int(stage.get("attemptCount") or 0),
            retry_path=str(stage.get("retryPath") or "clean"),
            result_impact=str(stage.get("resultImpact") or "none"),
            outcome=self._outcome(stage, incident_types),
            incident_types=incident_types,
            source="qualityFidelity.stageSummaries",
        )

    def _outcome(self, stage: dict[str, Any], incident_types: tuple[str, ...]) -> str:
        retry_path = str(stage.get("retryPath") or "clean")
        result_impact = str(stage.get("resultImpact") or "none")
        if result_impact == "stepFailed":
            return "failed"
        if "payloadTooLarge" in incident_types:
            return "payloadTooLarge"
        if "contextOverBudget" in incident_types:
            return "contextOverBudget"
        if result_impact in {"stepDegraded", "providerIncident"}:
            return "degraded"
        if retry_path in {"retryRecovered", "backupRecovered", "fallbackRecovered"}:
            return retry_path
        if retry_path == "providerError":
            return "degraded"
        return "clean"

    def _operation_kind(self, operation_id: str) -> str:
        if ":" in operation_id:
            return operation_id.split(":", 1)[0]
        return operation_id or "unknown"

    def _execution_mode(self, request_payload: dict[str, Any], steps: list[dict[str, Any]]) -> str | None:
        for candidate in [
            request_payload.get("executionMode"),
            _dict(request_payload.get("draftRunBudget")).get("executionMode"),
        ]:
            if candidate:
                return str(candidate)
        for _, payload in _walk_dicts({"steps": steps}):
            if payload.get("executionMode"):
                return str(payload["executionMode"])
        return None

    def _ai_run_payload(self, run: AiRun) -> dict[str, Any]:
        return {
            "id": run.id,
            "step": run.request_payload.get("draftRunStep"),
            "provider": run.provider.value,
            "model": run.model,
            "requestPayload": run.request_payload,
            "resultPayload": run.result_payload,
            "error": run.error,
            "fallbackUsed": run.fallback_used,
        }


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


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _canonical_incident_types(value: Any) -> tuple[str, ...]:
    incidents = tuple(str(item) for item in _list(value) if item)
    if "unknownProviderFailure" in incidents and len(set(incidents)) > 1:
        return tuple(item for item in incidents if item != "unknownProviderFailure")
    return incidents


def _optional_str(value: Any) -> str | None:
    return str(value) if value not in {None, ""} else None
