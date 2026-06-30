from __future__ import annotations

from fastapi import APIRouter

from backend.app.api.portfolio_auth import router as auth_router
from backend.app.api.portfolio_projects import router as projects_router

router = APIRouter(prefix="/api")
router.include_router(auth_router)
router.include_router(projects_router)
