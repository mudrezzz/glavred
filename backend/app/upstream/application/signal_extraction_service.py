"""Owner: upstream.application

Used by: RadarRun orchestration and explicit extraction retry API.
Does not own: provider attempt mechanics, web search, URL reading, project scoring, or UI.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.settings import BackendSettings
from backend.app.upstream.application.provider_budget_profiles import UpstreamProviderBudgetProfileRegistry
from backend.app.upstream.application.signal_extraction_attempts import SignalExtractionAttemptRunner
from backend.app.upstream.application.signal_extraction_context import (
    SignalExtractionContextFactory,
    SignalExtractionDossierFactory,
)
from backend.app.upstream.application.signal_extraction_provider import SignalExtractionProvider
from backend.app.upstream.application.signal_extraction_report import (
    SignalExtractionReportBuilder,
    SignalExtractionResultPresenter,
)


class SignalExtractionService:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        provider: SignalExtractionProvider,
        ai_run_service: AiRunService,
    ) -> None:
        self._settings = settings
        self._profiles = UpstreamProviderBudgetProfileRegistry()
        self._context = SignalExtractionContextFactory()
        self._dossiers = SignalExtractionDossierFactory()
        self._attempts = SignalExtractionAttemptRunner(provider=provider, ai_run_service=ai_run_service)
        self._reports = SignalExtractionReportBuilder()
        self._presenter = SignalExtractionResultPresenter()

    def extract(
        self,
        *,
        workspace: dict[str, Any],
        radar: dict[str, Any],
        run: dict[str, Any],
        materials: list[dict[str, Any]],
        previous_report: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        profile = self._profiles.resolve(
            operation_id="signalExtraction",
            execution_mode=self._settings.draft_run_execution_mode,
        )
        dossier = self._dossiers.build(
            context=self._context.build(workspace=workspace, radar=radar),
            materials=materials,
            profile=profile,
        )
        revision, prior_revisions = self._revision(previous_report)
        if dossier.readiness == "BLOCKED":
            outcome = self._reports.build(
                materials=materials,
                dossier=dossier,
                signals=[],
                provider_decisions=[],
                attempts=[],
                status="notRun",
                revision=revision,
                prior_revisions=prior_revisions,
                warnings=["signal-extraction-no-readable-fragments"],
            )
            return self._presenter.present(outcome=outcome, materials=materials, dossier=dossier, run=run)

        primary_model = self._settings.upstream_signal_extraction_model_or_default
        backup_model = self._settings.openrouter_backup_model_or_none
        if not self._settings.has_openrouter_api_key or not primary_model:
            outcome = self._reports.build(
                materials=materials,
                dossier=dossier,
                signals=[],
                provider_decisions=[],
                attempts=[],
                status="notRun",
                revision=revision,
                prior_revisions=prior_revisions,
                warnings=["signal-extraction-provider-not-configured"],
            )
            return self._presenter.present(outcome=outcome, materials=materials, dossier=dossier, run=run)

        trace: list[dict[str, Any]] = []
        grounding_violations: list[dict[str, Any]] = []
        repair_errors: list[str] = []
        specs = [("primary", primary_model), ("repair", primary_model)]
        if backup_model and backup_model != primary_model:
            specs.append(("backup", backup_model))
        for label, model in specs:
            attempt = self._attempts.run(
                dossier=dossier,
                profile=profile,
                label=label,
                model=model,
                radar_id=str(radar.get("id") or ""),
                run_id=str(run.get("id") or ""),
                repair_errors=repair_errors,
            )
            trace.append(attempt.attempt)
            grounding_violations.extend(attempt.grounding_violations)
            if attempt.accepted:
                outcome = self._reports.build(
                    materials=materials,
                    dossier=dossier,
                    signals=list(attempt.signals),
                    provider_decisions=list(attempt.decisions),
                    attempts=trace,
                    status="succeeded",
                    revision=revision,
                    prior_revisions=prior_revisions,
                    grounding_violations=grounding_violations,
                    warnings=["legacy-summary-only"] if dossier.legacy_material_ids else [],
                )
                return self._presenter.present(outcome=outcome, materials=materials, dossier=dossier, run=run)
            repair_errors = list(attempt.errors)
            if attempt.attempt.get("status") == "blocked":
                break

        outcome = self._reports.build(
            materials=materials,
            dossier=dossier,
            signals=[],
            provider_decisions=[],
            attempts=trace,
            status="failed",
            revision=revision,
            prior_revisions=prior_revisions,
            warnings=["signal-extraction-safe-no-signal-fallback"],
            grounding_violations=grounding_violations,
        )
        return self._presenter.present(outcome=outcome, materials=materials, dossier=dossier, run=run)

    def _revision(self, previous: dict[str, Any] | None) -> tuple[int, list[dict[str, Any]]]:
        revision = int((previous or {}).get("revision") or 0) + 1
        history = list((previous or {}).get("revisions") or [])
        if previous and (not history or history[-1].get("revision") != previous.get("revision")):
            history.append({"revision": previous.get("revision"), "status": previous.get("status")})
        return revision, history


__all__ = ("SignalExtractionService",)
