from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from backend.app.api.portfolio_contracts import (
    CreateProjectRequest,
    SaveWorkspaceRequest,
    UpdateProjectRequest,
    project_access_response,
    workspace_response,
)
from backend.app.api.portfolio_dependencies import current_user, portfolio_service
from backend.app.application.portfolio_service import AccessDeniedError, PortfolioService
from backend.app.domain.portfolio import UserAccount
from backend.app.portfolio.application.workspace_integrity import WorkspaceIntegrityError

router = APIRouter()


@router.get("/projects")
def projects(
    includeArchived: bool = False,
    user: UserAccount = Depends(current_user),
    service: PortfolioService = Depends(portfolio_service),
) -> dict[str, Any]:
    items = [
        project_access_response(project, membership)
        for project, membership in service.list_projects(user, include_archived=includeArchived)
    ]
    return {"projects": [item.model_dump(by_alias=True) for item in items]}


@router.post("/projects")
def create_project(
    payload: CreateProjectRequest,
    user: UserAccount = Depends(current_user),
    service: PortfolioService = Depends(portfolio_service),
) -> dict[str, Any]:
    project_item, membership = service.create_project(
        user,
        title=payload.title,
        description=payload.description,
        language=payload.language,
    )
    return project_access_response(project_item, membership).model_dump(by_alias=True)


@router.get("/projects/{project_id}")
def project(
    project_id: str,
    user: UserAccount = Depends(current_user),
    service: PortfolioService = Depends(portfolio_service),
) -> dict[str, Any]:
    try:
        project_item, membership = service.get_project(user, project_id)
    except AccessDeniedError as exc:
        raise HTTPException(status_code=403, detail="project-access-denied") from exc
    return project_access_response(project_item, membership).model_dump(by_alias=True)


@router.patch("/projects/{project_id}")
def update_project(
    project_id: str,
    payload: UpdateProjectRequest,
    user: UserAccount = Depends(current_user),
    service: PortfolioService = Depends(portfolio_service),
) -> dict[str, Any]:
    try:
        project_item, membership = service.update_project(
            user,
            project_id,
            title=payload.title,
            description=payload.description,
            status=payload.status,
        )
    except AccessDeniedError as exc:
        raise HTTPException(status_code=403, detail="project-access-denied") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return project_access_response(project_item, membership).model_dump(by_alias=True)


@router.get("/projects/{project_id}/workspace")
def workspace(
    project_id: str,
    user: UserAccount = Depends(current_user),
    service: PortfolioService = Depends(portfolio_service),
) -> dict[str, Any]:
    try:
        snapshot = service.get_workspace(user, project_id)
    except AccessDeniedError as exc:
        raise HTTPException(status_code=403, detail="project-access-denied") from exc
    except WorkspaceIntegrityError as exc:
        raise HTTPException(status_code=409, detail=exc.to_payload()) from exc
    return workspace_response(snapshot).model_dump(by_alias=True)


@router.put("/projects/{project_id}/workspace")
def save_workspace(
    project_id: str,
    payload: SaveWorkspaceRequest,
    user: UserAccount = Depends(current_user),
    service: PortfolioService = Depends(portfolio_service),
) -> dict[str, Any]:
    try:
        snapshot = service.save_workspace(user, project_id, payload.workspace)
    except AccessDeniedError as exc:
        raise HTTPException(status_code=403, detail="project-access-denied") from exc
    except WorkspaceIntegrityError as exc:
        raise HTTPException(status_code=422, detail=exc.to_payload()) from exc
    return workspace_response(snapshot).model_dump(by_alias=True)
