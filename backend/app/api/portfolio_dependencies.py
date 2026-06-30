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
    settings = portfolio_settings(request)
    return SQLitePortfolioRepository(settings.portfolio_db_path)


def portfolio_auth_service(request: Request) -> PortfolioAuthService:
    return PortfolioAuthService(portfolio_repository(request), portfolio_settings(request))


def portfolio_service(request: Request) -> PortfolioService:
    return PortfolioService(portfolio_repository(request))


def current_user(
    request: Request,
    service: PortfolioAuthService = Depends(portfolio_auth_service),
) -> UserAccount:
    token = request.cookies.get(portfolio_settings(request).glavred_session_cookie_name)
    try:
        return service.current_user(token)
    except AuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
