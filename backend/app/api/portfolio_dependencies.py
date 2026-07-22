from __future__ import annotations

from fastapi import Depends, HTTPException, Request

from backend.app.application.portfolio_auth_service import PortfolioAuthService
from backend.app.application.portfolio_service import AuthError, PortfolioService
from backend.app.domain.portfolio import UserAccount
from backend.app.infrastructure.sqlite_portfolio_repository import SQLitePortfolioRepository
from backend.app.settings import BackendSettings


def portfolio_settings(request: Request) -> BackendSettings:
    return request.app.state.settings


def portfolio_repository(request: Request) -> SQLitePortfolioRepository:
    cached = getattr(request.app.state, "portfolio_repository", None)
    if cached is not None:
        return cached
    settings = portfolio_settings(request)
    with request.app.state.portfolio_components_lock:
        cached = getattr(request.app.state, "portfolio_repository", None)
        if cached is None:
            cached = SQLitePortfolioRepository(settings.portfolio_db_path)
            request.app.state.portfolio_repository = cached
    return cached


def portfolio_auth_service(request: Request) -> PortfolioAuthService:
    cached = getattr(request.app.state, "portfolio_auth_service", None)
    if cached is not None:
        return cached
    repository = portfolio_repository(request)
    with request.app.state.portfolio_components_lock:
        cached = getattr(request.app.state, "portfolio_auth_service", None)
        if cached is None:
            cached = PortfolioAuthService(repository, portfolio_settings(request))
            request.app.state.portfolio_auth_service = cached
    return cached


def portfolio_service(request: Request) -> PortfolioService:
    cached = getattr(request.app.state, "portfolio_service", None)
    if cached is not None:
        return cached
    repository = portfolio_repository(request)
    with request.app.state.portfolio_components_lock:
        cached = getattr(request.app.state, "portfolio_service", None)
        if cached is None:
            cached = PortfolioService(repository)
            request.app.state.portfolio_service = cached
    return cached


def current_user(
    request: Request,
    service: PortfolioAuthService = Depends(portfolio_auth_service),
) -> UserAccount:
    token = request.cookies.get(portfolio_settings(request).glavred_session_cookie_name)
    try:
        return service.current_user(token)
    except AuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
