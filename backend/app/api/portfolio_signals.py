"""Owner: api

Used by: authenticated portfolio clients for signal scoring and human review commands.
Does not own: scoring semantics, review transitions, provider transport, or SQLite mapping.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from backend.app.api.portfolio_dependencies import current_user, portfolio_service
from backend.app.application.ai_run_service import AiRunService
from backend.app.application.portfolio_service import AccessDeniedError, PortfolioService
from backend.app.domain.portfolio import UserAccount
from backend.app.infrastructure.openrouter_signal_utility_adapter import OpenRouterSignalUtilityAdapter
from backend.app.infrastructure.sqlite_ai_run_repository import SqliteAiRunRepository
from backend.app.upstream.application.legacy_signal_integrity import LegacySignalIntegrityPolicy
from backend.app.upstream.application.signal_review_lifecycle import SourceSignalReviewLifecyclePolicy
from backend.app.upstream.application.signal_utility_service import SignalUtilityScoringService
from backend.app.upstream.domain.signal_review import SourceSignalReviewCommand, SourceSignalReviewError

router = APIRouter()


class SignalReviewRequest(BaseModel):
    action: str
    reason: str = ""
    editorial_patch: dict[str, str] = Field(default_factory=dict, alias="editorialPatch")
    expected_review_revision: int = Field(default=0, alias="expectedReviewRevision")

    model_config = {"populate_by_name": True}


class SignalScoringResponse(BaseModel):
    run: dict[str, Any]
    sourceSignals: list[dict[str, Any]]
    signalScoringReport: dict[str, Any]


class SignalReviewResponse(BaseModel):
    sourceSignal: dict[str, Any]
    signalScoringReport: dict[str, Any] | None = None


def signal_utility_service(request: Request) -> SignalUtilityScoringService:
    settings = request.app.state.settings
    provider = getattr(request.app.state, "signal_utility_provider", None) or OpenRouterSignalUtilityAdapter(settings=settings)
    return SignalUtilityScoringService(
        settings=settings,
        provider=provider,
        ai_run_service=AiRunService(repository=SqliteAiRunRepository(settings.ai_run_audit_db_path)),
    )


@router.post("/projects/{project_id}/radar-runs/{run_id}/signal-scoring")
def rescore_signals(
    project_id: str,
    run_id: str,
    user: UserAccount = Depends(current_user),
    portfolio: PortfolioService = Depends(portfolio_service),
    scoring: SignalUtilityScoringService = Depends(signal_utility_service),
) -> SignalScoringResponse:
    workspace, project = _workspace(portfolio, user, project_id)
    run = _find(workspace.get("radarRuns"), run_id)
    if not run:
        raise HTTPException(status_code=404, detail="radar-run-not-found")
    radar = _find(workspace.get("radars"), str(run.get("radarId") or ""))
    if not radar:
        raise HTTPException(status_code=404, detail="radar-not-found")
    signals = _eligible_scoring_signals([
        item for item in workspace.get("sourceSignals", [])
        if isinstance(item, dict) and item.get("radarRunId") == run_id
    ])
    if not signals:
        raise HTTPException(status_code=409, detail="signal-reextraction-required")
    result = scoring.score(
        workspace=workspace,
        radar=radar,
        run=run,
        signals=signals,
        project_context={"projectId": project_id, "editorialLanguage": project.language},
        previous_report=run.get("signalScoring") if isinstance(run.get("signalScoring"), dict) else None,
    )
    updated_run = _run_with_scoring(run, result)
    workspace["radarRuns"] = _replace(workspace.get("radarRuns"), updated_run)
    workspace["sourceSignals"] = _merge_signals(workspace.get("sourceSignals"), result["sourceSignals"])
    portfolio.save_workspace(user, project_id, workspace)
    return SignalScoringResponse(
        run=updated_run,
        sourceSignals=result["sourceSignals"],
        signalScoringReport=result["signalScoringReport"],
    )


@router.post("/projects/{project_id}/source-signals/{signal_id}/review")
def review_signal(
    project_id: str,
    signal_id: str,
    payload: SignalReviewRequest,
    user: UserAccount = Depends(current_user),
    portfolio: PortfolioService = Depends(portfolio_service),
    scoring: SignalUtilityScoringService = Depends(signal_utility_service),
) -> SignalReviewResponse:
    workspace, project = _workspace(portfolio, user, project_id)
    policy = LegacySignalIntegrityPolicy()
    existing = _find(workspace.get("sourceSignals"), signal_id)
    if not existing:
        raise HTTPException(status_code=404, detail="source-signal-not-found")
    existing = policy.normalize(existing) if not existing.get("editorialLanguage") else existing
    try:
        reviewed = SourceSignalReviewLifecyclePolicy().apply(
            existing,
            SourceSignalReviewCommand(
                action=payload.action,
                actor_id=user.id,
                reason=payload.reason,
                expected_revision=payload.expected_review_revision,
                editorial_patch=payload.editorial_patch,
            ),
        )
    except SourceSignalReviewError as exc:
        status = 409 if exc.code == "signal-review-revision-conflict" else 422
        raise HTTPException(status_code=status, detail=exc.code) from exc
    updated_signal = reviewed.signal
    scoring_report = None
    if reviewed.utility_stale and updated_signal.get("radarRunId"):
        run = _find(workspace.get("radarRuns"), str(updated_signal.get("radarRunId")))
        radar = _find(workspace.get("radars"), str(updated_signal.get("radarId") or ""))
        if run and radar:
            run_signals = [
                updated_signal if item.get("id") == signal_id else item
                for item in workspace.get("sourceSignals", [])
                if isinstance(item, dict) and item.get("radarRunId") == run.get("id")
            ]
            eligible_signals = _eligible_scoring_signals(run_signals)
            result = scoring.score(
                workspace=workspace,
                radar=radar,
                run=run,
                signals=eligible_signals,
                project_context={"projectId": project_id, "editorialLanguage": project.language},
                previous_report=run.get("signalScoring") if isinstance(run.get("signalScoring"), dict) else None,
            )
            updated_signal = _find(result["sourceSignals"], signal_id) or updated_signal
            updated_run = _run_with_scoring(run, result)
            workspace["radarRuns"] = _replace(workspace.get("radarRuns"), updated_run)
            workspace["sourceSignals"] = _merge_signals(workspace.get("sourceSignals"), result["sourceSignals"])
            scoring_report = result["signalScoringReport"]
    workspace["sourceSignals"] = _replace(workspace.get("sourceSignals"), updated_signal)
    if workspace.get("sourceSignal", {}).get("id") == signal_id:
        workspace["sourceSignal"] = updated_signal
    portfolio.save_workspace(user, project_id, workspace)
    return SignalReviewResponse(sourceSignal=updated_signal, signalScoringReport=scoring_report)


def _workspace(portfolio: PortfolioService, user: UserAccount, project_id: str) -> tuple[dict[str, Any], Any]:
    try:
        project, _membership = portfolio.get_project(user, project_id)
        snapshot = portfolio.get_workspace(user, project_id)
    except AccessDeniedError as exc:
        raise HTTPException(status_code=403, detail="project-access-denied") from exc
    return deepcopy(snapshot.payload), project


def _find(items: Any, item_id: str) -> dict[str, Any] | None:
    if not isinstance(items, list):
        return None
    return next((item for item in items if isinstance(item, dict) and item.get("id") == item_id), None)


def _replace(items: Any, replacement: dict[str, Any]) -> list[dict[str, Any]]:
    source = [item for item in items if isinstance(item, dict)] if isinstance(items, list) else []
    return [replacement if item.get("id") == replacement.get("id") else item for item in source]


def _merge_signals(items: Any, replacements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {str(item.get("id") or ""): item for item in replacements}
    source = [item for item in items if isinstance(item, dict)] if isinstance(items, list) else []
    return [by_id.get(str(item.get("id") or ""), item) for item in source]


def _eligible_scoring_signals(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        item
        for item in signals
        if item.get("editorialLanguage") and item.get("evidenceRefs")
    ]


def _run_with_scoring(run: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    operations = [*list(run.get("operations") or []), result["operation"]]
    return {
        **run,
        "signalScoring": result["signalScoringReport"],
        "operations": operations,
        "budget": {**dict(run.get("budget") or {}), "usedOperations": len(operations)},
    }


__all__ = ("router",)
