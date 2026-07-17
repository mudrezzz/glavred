from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.openrouter_web_search_adapter import OpenRouterWebSearchAdapter
from backend.app.infrastructure.public_url_reader import HttpxPublicUrlReader
from backend.app.infrastructure.sqlite_ai_run_repository import SqliteAiRunRepository
from backend.app.application.ai_run_service import AiRunService
from backend.app.upstream.application.external_run_service import UpstreamRadarExternalRunService
from backend.app.upstream.application.signal_extraction_service import SignalExtractionService
from backend.app.infrastructure.openrouter_signal_extraction_adapter import OpenRouterSignalExtractionAdapter

router = APIRouter(prefix="/api/radar-runs")


class RadarProjectContext(BaseModel):
    project_id: str = Field(alias="projectId")
    editorial_language: str = Field(alias="editorialLanguage")

    model_config = {"populate_by_name": True}


class RadarRunExternalRequest(BaseModel):
    radar_id: str = Field(alias="radarId")
    workspace: dict[str, Any]
    project_context: RadarProjectContext | None = Field(default=None, alias="projectContext")

    model_config = {"populate_by_name": True}


class RadarRunExternalResponse(BaseModel):
    radar: dict[str, Any]
    run: dict[str, Any]
    found_materials: list[dict[str, Any]] = Field(alias="foundMaterials")
    source_signals: list[dict[str, Any]] = Field(default_factory=list, alias="sourceSignals")
    signal_extraction_report: dict[str, Any] = Field(default_factory=dict, alias="signalExtractionReport")

    model_config = {"populate_by_name": True}


class SignalExtractionRetryRequest(BaseModel):
    workspace: dict[str, Any]
    force_retry: bool = Field(default=False, alias="forceRetry")
    project_context: RadarProjectContext | None = Field(default=None, alias="projectContext")

    model_config = {"populate_by_name": True}


class SignalExtractionRetryResponse(BaseModel):
    run: dict[str, Any]
    source_signals: list[dict[str, Any]] = Field(alias="sourceSignals")
    signal_extraction_report: dict[str, Any] = Field(alias="signalExtractionReport")

    model_config = {"populate_by_name": True}


def create_upstream_radar_external_run_service(request: Request) -> UpstreamRadarExternalRunService:
    web_search_adapter = getattr(request.app.state, "openrouter_web_search_adapter", None) or OpenRouterWebSearchAdapter()
    url_reader = getattr(request.app.state, "public_url_reader", None) or HttpxPublicUrlReader()
    settings = request.app.state.settings
    signal_provider = getattr(request.app.state, "signal_extraction_provider", None) or OpenRouterSignalExtractionAdapter(settings=settings)
    signal_service = SignalExtractionService(
        settings=settings,
        provider=signal_provider,
        ai_run_service=AiRunService(repository=SqliteAiRunRepository(settings.ai_run_audit_db_path)),
    )
    return UpstreamRadarExternalRunService(
        settings=settings,
        web_search_adapter=web_search_adapter,
        url_reader=url_reader,
        openrouter_validator=OpenRouterConfigValidator(),
        signal_extraction_service=signal_service,
    )


@router.post("/external", response_model=RadarRunExternalResponse, response_model_by_alias=True)
def run_external_radar(
    payload: RadarRunExternalRequest,
    service: UpstreamRadarExternalRunService = Depends(create_upstream_radar_external_run_service),
) -> RadarRunExternalResponse:
    try:
        result = service.run(
            workspace=payload.workspace,
            radar_id=payload.radar_id,
            project_context=payload.project_context.model_dump(by_alias=True) if payload.project_context else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail={"message": str(exc)}) from exc
    return RadarRunExternalResponse(
        radar=result["radar"],
        run=result["run"],
        foundMaterials=result["foundMaterials"],
        sourceSignals=result["sourceSignals"],
        signalExtractionReport=result["signalExtractionReport"],
    )


@router.post("/{run_id}/signal-extraction", response_model=SignalExtractionRetryResponse, response_model_by_alias=True)
def retry_signal_extraction(
    run_id: str,
    payload: SignalExtractionRetryRequest,
    service: UpstreamRadarExternalRunService = Depends(create_upstream_radar_external_run_service),
) -> SignalExtractionRetryResponse:
    try:
        result = service.retry_signal_extraction(
            workspace=payload.workspace,
            run_id=run_id,
            force_retry=payload.force_retry,
            project_context=payload.project_context.model_dump(by_alias=True) if payload.project_context else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail={"message": str(exc)}) from exc
    return SignalExtractionRetryResponse(
        run=result["run"],
        sourceSignals=result["sourceSignals"],
        signalExtractionReport=result["signalExtractionReport"],
    )
