"""Owner: drafting.application.quality

Used by: DraftRun workflow completion and diagnostics tooling.
Does not own: provider transport, validation/revision decisions, prompt text, or UI layout.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from typing import Any

from backend.app.domain.draft_run import DraftRun
from backend.app.drafting.application.quality.evidence_fidelity_component import (
    QualityFidelityEvidenceComponent,
)
from backend.app.drafting.application.quality.issue_lifecycle_component import (
    QualityFidelityIssueComponent,
)
from backend.app.drafting.application.quality.stage_recovery_component import (
    QualityFidelityStageRecoveryComponent,
)
from backend.app.drafting.application.quality.verdict_policy import QualityFidelityVerdictPolicy


class DraftRunQualityFidelityReporter:
    """Coordinates quality/fidelity components into one trace-safe report."""

    def __init__(
        self,
        *,
        stages: QualityFidelityStageRecoveryComponent | None = None,
        evidence: QualityFidelityEvidenceComponent | None = None,
        issues: QualityFidelityIssueComponent | None = None,
        verdicts: QualityFidelityVerdictPolicy | None = None,
    ) -> None:
        self._stages = stages or QualityFidelityStageRecoveryComponent()
        self._evidence = evidence or QualityFidelityEvidenceComponent()
        self._issues = issues or QualityFidelityIssueComponent()
        self._verdicts = verdicts or QualityFidelityVerdictPolicy()

    def build_from_run(
        self,
        run: DraftRun | None,
        *,
        final_draft: dict[str, Any] | None = None,
        ai_runs: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        steps = [
            {
                "key": step.key.value,
                "status": step.status.value,
                "error": step.error,
                "artifact": step.artifact_payload or {},
            }
            for step in (run.steps if run else [])
        ]
        return self.build(
            run_status=str(run.status.value if run else "unknown"),
            steps=steps,
            final_draft=final_draft if final_draft is not None else run.final_draft if run else None,
            ai_runs=ai_runs,
        )

    def build(
        self,
        *,
        run_status: str,
        steps: list[dict[str, Any]],
        final_draft: dict[str, Any] | None,
        ai_runs: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        stage_summaries = self._stages.stage_summaries(steps, ai_runs or [])
        evidence = self._evidence.summary(steps, stage_summaries)
        issue_lifecycle = self._issues.summary(steps)
        technical_status = self._verdicts.technical_status(run_status, steps, final_draft)
        provider_status = self._verdicts.provider_recovery_status(stage_summaries)
        editorial_status = self._verdicts.editorial_status(
            technical_status=technical_status,
            issue_lifecycle=issue_lifecycle,
            evidence=evidence,
            final_gate=self._issues.final_gate(steps),
            final_draft=final_draft,
        )
        return {
            "version": "draft-run-quality-fidelity-v1",
            "technicalStatus": technical_status,
            "providerRecoveryStatus": provider_status,
            "editorialStatus": editorial_status,
            "overallVerdict": self._verdicts.overall_verdict(technical_status, provider_status, editorial_status),
            "stageSummaries": stage_summaries,
            "evidenceFidelity": evidence,
            "issueLifecycle": issue_lifecycle,
        }
