from __future__ import annotations

import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from backend.app.domain.portfolio import BlogProject, ProjectMembership, Session, UserAccount, WorkspaceSnapshot
from backend.app.infrastructure.sqlite_portfolio_repository import SQLitePortfolioRepository
from backend.app.settings import BackendSettings


class AuthError(Exception):
    pass


class AccessDeniedError(Exception):
    pass


class PortfolioService:
    def __init__(self, repository: SQLitePortfolioRepository, settings: BackendSettings) -> None:
        self._repository = repository
        self._settings = settings
        self._repository.ensure_seeded()

    def login(self, email: str, password: str) -> tuple[UserAccount, Session]:
        if self._settings.glavred_auth_mode != "dev-password":
            raise AuthError("unsupported-auth-mode")
        user = self._repository.get_user_by_email(email.strip())
        if user is None or user.status != "active":
            raise AuthError("invalid-credentials")
        expected = self._settings.glavred_dev_auth_password.get_secret_value()
        if not hmac.compare_digest(password, expected):
            raise AuthError("invalid-credentials")
        expires_at = datetime.now(UTC) + timedelta(hours=max(1, self._settings.glavred_session_ttl_hours))
        session = self._repository.create_session(secrets.token_urlsafe(32), user.id, expires_at)
        return user, session

    def logout(self, token: str | None) -> None:
        if token:
            self._repository.delete_session(token)

    def current_user(self, token: str | None) -> UserAccount:
        if not token:
            raise AuthError("missing-session")
        session = self._repository.get_session(token)
        if session is None:
            raise AuthError("invalid-session")
        user = self._repository.get_user(session.user_id)
        if user is None or user.status != "active":
            raise AuthError("invalid-session")
        return user

    def list_projects(self, user: UserAccount) -> list[tuple[BlogProject, ProjectMembership]]:
        return self._repository.list_projects_for_user(user.id)

    def get_project(self, user: UserAccount, project_id: str) -> tuple[BlogProject, ProjectMembership]:
        item = self._repository.get_project_for_user(user.id, project_id)
        if item is None:
            raise AccessDeniedError("project-access-denied")
        return item

    def get_workspace(self, user: UserAccount, project_id: str) -> WorkspaceSnapshot:
        self.get_project(user, project_id)
        snapshot = self._repository.latest_workspace_snapshot(project_id)
        if snapshot is None:
            return self._repository.save_workspace_snapshot(project_id, {})
        return snapshot

    def save_workspace(self, user: UserAccount, project_id: str, payload: dict[str, Any]) -> WorkspaceSnapshot:
        self.get_project(user, project_id)
        return self._repository.save_workspace_snapshot(project_id, payload)
