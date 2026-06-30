from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from backend.app.api.portfolio_contracts import LoginRequest, user_response
from backend.app.api.portfolio_dependencies import current_user, portfolio_auth_service, portfolio_settings
from backend.app.application.portfolio_auth_service import PortfolioAuthService
from backend.app.application.portfolio_service import AuthError
from backend.app.domain.portfolio import UserAccount

router = APIRouter()


@router.post("/auth/login")
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    service: PortfolioAuthService = Depends(portfolio_auth_service),
) -> dict[str, Any]:
    try:
        user, session = service.login(payload.email, payload.password)
    except AuthError as exc:
        raise HTTPException(status_code=401, detail="invalid-credentials") from exc
    settings = portfolio_settings(request)
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
def logout(
    request: Request,
    response: Response,
    service: PortfolioAuthService = Depends(portfolio_auth_service),
) -> dict[str, str]:
    cookie_name = portfolio_settings(request).glavred_session_cookie_name
    service.logout(request.cookies.get(cookie_name))
    response.delete_cookie(key=cookie_name, httponly=True, samesite="lax", secure=False)
    return {"status": "ok"}


@router.get("/users/me")
def me(user: UserAccount = Depends(current_user)) -> dict[str, Any]:
    return {"user": user_response(user).model_dump(by_alias=True)}
