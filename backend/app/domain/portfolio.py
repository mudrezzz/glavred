from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class UserAccount:
    id: str
    display_name: str
    email: str
    avatar_url: str | None
    status: str
    created_at: datetime


@dataclass(frozen=True)
class ProjectMembership:
    id: str
    user_id: str
    project_id: str
    role: str
    status: str


@dataclass(frozen=True)
class BlogProject:
    id: str
    owner_user_id: str
    title: str
    description: str
    language: str
    status: str
    benchmark_role: str | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class WorkspaceSnapshot:
    id: str
    project_id: str
    payload: dict[str, Any]
    created_at: datetime


@dataclass(frozen=True)
class Session:
    token: str
    user_id: str
    expires_at: datetime
    created_at: datetime
