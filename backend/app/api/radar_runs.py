from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.openrouter_web_search_adapter import OpenRouterWebSearchAdapter
from backend.app.infrastructure.public_url_reader import HttpxPublicUrlReader
from backend.app.upstream.application.external_run_service import UpstreamRadarExternalRunService

router = APIRouter(prefix="/api/radar-runs")


class RadarRunExternalRequest(BaseModel):
    radar_id: str = Field(alias="radarId")
    workspace: dict[str, Any]


class RadarRunExternalResponse(BaseModel):
    radar: dict[str, Any]
    run: dict[str, Any]
    found_materials: list[dict[str, Any]] = Field(alias="foundMaterials")

    model_config = {"populate_by_name": True}


def create_upstream_radar_external_run_service(request: Request) -> UpstreamRadarExternalRunService:
    web_search_adapter = getattr(request.app.state, "openrouter_web_search_adapter", None) or OpenRouterWebSearchAdapter()
    url_reader = getattr(request.app.state, "public_url_reader", None) or HttpxPublicUrlReader()
    return UpstreamRadarExternalRunService(
        settings=request.app.state.settings,
        web_search_adapter=web_search_adapter,
        url_reader=url_reader,
        openrouter_validator=OpenRouterConfigValidator(),
    )


@router.post("/external", response_model=RadarRunExternalResponse, response_model_by_alias=True)
def run_external_radar(
    payload: RadarRunExternalRequest,
    service: UpstreamRadarExternalRunService = Depends(create_upstream_radar_external_run_service),
) -> RadarRunExternalResponse:
    try:
        result = service.run(workspace=payload.workspace, radar_id=payload.radar_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail={"message": str(exc)}) from exc
    return RadarRunExternalResponse(
        radar=result["radar"],
        run=result["run"],
        foundMaterials=result["foundMaterials"],
    )
