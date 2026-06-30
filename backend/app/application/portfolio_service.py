from __future__ import annotations

from typing import Any

from backend.app.domain.portfolio import BlogProject, ProjectMembership, UserAccount, WorkspaceSnapshot
from backend.app.infrastructure.sqlite_portfolio_repository import SQLitePortfolioRepository


class AuthError(Exception):
    pass


class AccessDeniedError(Exception):
    pass


class PortfolioService:
    def __init__(self, repository: SQLitePortfolioRepository) -> None:
        self._repository = repository
        self._repository.ensure_seeded()

    def list_projects(self, user: UserAccount, *, include_archived: bool = False) -> list[tuple[BlogProject, ProjectMembership]]:
        return self._repository.list_projects_for_user(user.id, include_archived=include_archived)

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

    def create_project(
        self,
        user: UserAccount,
        *,
        title: str,
        description: str = "",
        language: str = "ru",
    ) -> tuple[BlogProject, ProjectMembership]:
        clean_title = title.strip() or "New blog project"
        clean_language = language.strip() or "ru"
        return self._repository.create_project_for_user(
            user.id,
            title=clean_title,
            description=description.strip(),
            language=clean_language,
        )

    def update_project(
        self,
        user: UserAccount,
        project_id: str,
        *,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
    ) -> tuple[BlogProject, ProjectMembership]:
        self.get_project(user, project_id)
        if status is not None and status not in {"active", "archived"}:
            raise ValueError("invalid-project-status")
        self._repository.update_project(
            project_id,
            title=title.strip() if title is not None else None,
            description=description.strip() if description is not None else None,
            status=status,
        )
        updated = self._repository.get_project_for_user(user.id, project_id, include_archived=True)
        if updated is None:
            raise AccessDeniedError("project-access-denied")
        return updated
