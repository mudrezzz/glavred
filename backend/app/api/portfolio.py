from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from backend.app.api.portfolio_contracts import (
    LoginRequest,
    SaveWorkspaceRequest,
    project_access_response,
    user_response,
    workspace_response,
)
from backend.app.application.portfolio_service import AccessDeniedError, AuthError, PortfolioService
from backend.app.domain.portfolio import UserAccount
from backend.app.infrastructure.sqlite_portfolio_repository import SQLitePortfolioRepository
from backend.app.settings import BackendSettings

router = APIRouter(prefix="/api")


def _settings(request: Request) -> BackendSettings:
    return request.app.state.settings


def _service(request: Request) -> PortfolioService:
    settings = _settings(request)
    return PortfolioService(SQLitePortfolioRepository(settings.portfolio_db_path), settings)


def _current_user(request: Request, service: PortfolioService = Depends(_service)) -> UserAccount:
    token = request.cookies.get(_settings(request).glavred_session_cookie_name)
    try:
        return service.current_user(token)
    except AuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.post("/auth/login")
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    service: PortfolioService = Depends(_service),
) -> dict[str, Any]:
    try:
        user, session = service.login(payload.email, payload.password)
    except AuthError as exc:
        raise HTTPException(status_code=401, detail="invalid-credentials") from exc
    settings = _settings(request)
    response.set_cookie(
        key=settings.glavred_session_cookie_name,
        value=session.token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=max(1, settings.glavred_session_ttl_hours) * 3600,
    )
    return {"user": user_response(user).model_dump(by_alias=True)}


@router.post("/auth/logout")
def logout(request: Request, response: Response, service: PortfolioService = Depends(_service)) -> dict[str, str]:
    cookie_name = _settings(request).glavred_session_cookie_name
    service.logout(request.cookies.get(cookie_name))
    response.delete_cookie(key=cookie_name, httponly=True, samesite="lax", secure=False)
    return {"status": "ok"}


@router.get("/users/me")
def me(user: UserAccount = Depends(_current_user)) -> dict[str, Any]:
    return {"user": user_response(user).model_dump(by_alias=True)}


@router.get("/projects")
def projects(
    user: UserAccount = Depends(_current_user),
    service: PortfolioService = Depends(_service),
) -> dict[str, Any]:
    items = [project_access_response(project, membership) for project, membership in service.list_projects(user)]
    return {"projects": [item.model_dump(by_alias=True) for item in items]}


@router.get("/projects/{project_id}")
def project(
    project_id: str,
    user: UserAccount = Depends(_current_user),
    service: PortfolioService = Depends(_service),
) -> dict[str, Any]:
    try:
        project_item, membership = service.get_project(user, project_id)
    except AccessDeniedError as exc:
        raise HTTPException(status_code=403, detail="project-access-denied") from exc
    return project_access_response(project_item, membership).model_dump(by_alias=True)


@router.get("/projects/{project_id}/workspace")
def workspace(
    project_id: str,
    user: UserAccount = Depends(_current_user),
    service: PortfolioService = Depends(_service),
) -> dict[str, Any]:
    try:
        snapshot = service.get_workspace(user, project_id)
    except AccessDeniedError as exc:
        raise HTTPException(status_code=403, detail="project-access-denied") from exc
    return workspace_response(snapshot).model_dump(by_alias=True)


@router.put("/projects/{project_id}/workspace")
def save_workspace(
    project_id: str,
    payload: SaveWorkspaceRequest,
    user: UserAccount = Depends(_current_user),
    service: PortfolioService = Depends(_service),
) -> dict[str, Any]:
    try:
        snapshot = service.save_workspace(user, project_id, payload.workspace)
    except AccessDeniedError as exc:
        raise HTTPException(status_code=403, detail="project-access-denied") from exc
    return workspace_response(snapshot).model_dump(by_alias=True)
