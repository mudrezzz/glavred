"""Owner: upstream.application

Used by: RadarRun orchestration, extraction retry, and project-scoped manual scoring.
Does not own: search, extraction, human review transitions, persistence, or candidate assembly.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.settings import BackendSettings
from backend.app.upstream.application.provider_budget_profiles import (
    UpstreamProviderBudgetProfile,
    UpstreamProviderBudgetProfileRegistry,
)
from backend.app.upstream.application.signal_utility_attempts import SignalUtilityAttemptRunner
from backend.app.upstream.application.signal_utility_decision import SignalUtilityDecisionPolicy
from backend.app.upstream.application.signal_utility_dossier import SignalUtilityDossierFactory
from backend.app.upstream.application.signal_utility_profile import ProjectEditorialOpportunityProfileFactory
from backend.app.upstream.application.signal_utility_provider import SignalUtilityProvider
from backend.app.upstream.application.signal_utility_report import SignalUtilityReportBuilder
from backend.app.upstream.application.signal_relationships import SignalRelationshipPolicy
from backend.app.upstream.domain.signal_utility import (
    ProjectEditorialSetting,
    SignalUtilityDossier,
    SignalUtilityDimensionResult,
    SignalUtilityEvaluation,
)


class SignalUtilityScoringService:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        provider: SignalUtilityProvider,
        ai_run_service: AiRunService,
    ) -> None:
        self._settings = settings
        self._profiles = UpstreamProviderBudgetProfileRegistry()
        self._project_profiles = ProjectEditorialOpportunityProfileFactory()
        self._dossiers = SignalUtilityDossierFactory()
        self._attempts = SignalUtilityAttemptRunner(provider=provider, ai_run_service=ai_run_service)
        self._decisions = SignalUtilityDecisionPolicy()
        self._reports = SignalUtilityReportBuilder()
        self._relationships = SignalRelationshipPolicy()

    def score(
        self,
        *,
        workspace: dict[str, Any],
        radar: dict[str, Any],
        run: dict[str, Any],
        signals: list[dict[str, Any]],
        project_context: dict[str, Any] | None,
        previous_report: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        budget = self._profiles.resolve(
            operation_id="signalScoring",
            execution_mode=self._settings.draft_run_execution_mode,
        )
        project_profile = self._project_profiles.build(
            workspace=workspace,
            radar=radar,
            project_context=project_context,
        )
        revision = int((previous_report or {}).get("revision") or 0) + 1
        pending: list[
            tuple[
                dict[str, Any],
                tuple[SignalUtilityDimensionResult, ...] | None,
                str,
                tuple[ProjectEditorialSetting, ...],
            ]
        ] = []
        accepted_relationships: dict[str, dict[str, str]] = {}
        attempts: list[dict[str, Any]] = []
        dossiers: list[SignalUtilityDossier] = []
        batch_size = max(1, budget.max_materials)
        signal_batches = [signals[index:index + batch_size] for index in range(0, len(signals), batch_size)] or [[]]
        for batch_index, batch in enumerate(signal_batches, start=1):
            dossier = self._dossiers.build(profile=project_profile, signals=batch, budget=budget)
            dossiers.append(dossier)
            batch_pending, batch_attempts, batch_relationships = self._score_batch(
                signals=batch,
                dossier=dossier,
                budget=budget,
                setting_modes={item.id: item.mode for item in project_profile.settings},
                batch_index=batch_index,
            )
            retained_settings = tuple(
                item for item in project_profile.settings if item.id in dossier.setting_ids
            )
            pending.extend(
                (signal, dimensions, failure_reason, retained_settings)
                for signal, dimensions, failure_reason in batch_pending
            )
            attempts.extend(batch_attempts)
            accepted_relationships.update(batch_relationships)
        relationship_reports = self._relationships.reports(signals, accepted_relationships)
        evaluations: list[SignalUtilityEvaluation] = []
        for signal, provider_dimensions, failure_reason, retained_settings in pending:
            signal_id = str(signal.get("id") or "")
            evaluations.append(
                self._decisions.evaluate(
                    signal=signal,
                    provider_dimensions=provider_dimensions,
                    settings=retained_settings,
                    relationship_report=relationship_reports.get(signal_id),
                )
                if provider_dimensions is not None
                else self._decisions.inconclusive(
                    signal_id,
                    failure_reason,
                    relationship_report=relationship_reports.get(signal_id),
                )
            )
        return self._reports.build(
            run_id=str(run.get("id") or "manual-signal-scoring"),
            signals=signals,
            evaluations=evaluations,
            dossiers=dossiers,
            attempts=attempts,
            revision=revision,
            previous_report=previous_report,
        )

    def _score_batch(
        self,
        *,
        signals: list[dict[str, Any]],
        dossier: SignalUtilityDossier,
        budget: UpstreamProviderBudgetProfile,
        setting_modes: dict[str, str],
        batch_index: int,
    ) -> tuple[
        list[tuple[dict[str, Any], tuple[SignalUtilityDimensionResult, ...] | None, str]],
        list[dict[str, Any]],
        dict[str, dict[str, str]],
    ]:
        accepted_dimensions: dict[str, tuple[SignalUtilityDimensionResult, ...]] | None = None
        accepted_relationships: dict[str, dict[str, str]] = {}
        failure_reason = "signal-scoring-inconclusive"
        attempts: list[dict[str, Any]] = []
        primary_model = self._settings.upstream_signal_scoring_model_or_default
        if dossier.readiness != "BLOCKED" and self._settings.has_openrouter_api_key and primary_model:
            repair_errors: list[str] = []
            specs = [("primary", primary_model), ("repair", primary_model)]
            backup_model = self._settings.openrouter_backup_model_or_none
            if backup_model and backup_model != primary_model:
                specs.append(("backup", backup_model))
            for label, model in specs:
                attempt = self._attempts.run(
                    dossier=dossier,
                    profile=budget,
                    label=label,
                    model=model,
                    repair_errors=repair_errors,
                    setting_modes=setting_modes,
                )
                attempts.append({**attempt.attempt, "batchIndex": batch_index})
                if attempt.accepted:
                    accepted_dimensions = attempt.evaluations
                    accepted_relationships = attempt.relationships
                    break
                repair_errors = list(attempt.errors)
                failure_reason = repair_errors[0] if repair_errors else failure_reason
                if attempt.attempt.get("status") == "blocked":
                    break
        elif dossier.readiness == "BLOCKED":
            failure_reason = ",".join(dossier.missing_inputs) or "signal-utility-dossier-blocked"
        else:
            failure_reason = "signal-scoring-provider-not-configured"

        pending = [
            (signal, (accepted_dimensions or {}).get(str(signal.get("id") or "")), failure_reason)
            for signal in signals
        ]
        return pending, attempts, accepted_relationships


__all__ = ("SignalUtilityScoringService",)
