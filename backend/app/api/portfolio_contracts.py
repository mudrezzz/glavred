from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.app.domain.portfolio import BlogProject, ProjectMembership, UserAccount, WorkspaceSnapshot


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    display_name: str = Field(alias="displayName")
    email: str
    avatar_url: str | None = Field(alias="avatarUrl")
    status: str
    created_at: str = Field(alias="createdAt")


class ProjectResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    owner_user_id: str = Field(alias="ownerUserId")
    title: str
    description: str
    language: str
    status: str
    benchmark_role: str | None = Field(alias="benchmarkRole")
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")


class MembershipResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    user_id: str = Field(alias="userId")
    project_id: str = Field(alias="projectId")
    role: str
    status: str


class ProjectAccessResponse(BaseModel):
    project: ProjectResponse
    membership: MembershipResponse


class WorkspaceResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    project_id: str = Field(alias="projectId")
    workspace: dict[str, Any]
    created_at: str = Field(alias="createdAt")


class SaveWorkspaceRequest(BaseModel):
    workspace: dict[str, Any]


class CreateProjectRequest(BaseModel):
    title: str
    description: str = ""
    language: str = "ru"


class UpdateProjectRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None


def user_response(user: UserAccount) -> UserResponse:
    return UserResponse(
        id=user.id,
        displayName=user.display_name,
        email=user.email,
        avatarUrl=user.avatar_url,
        status=user.status,
        createdAt=_dt(user.created_at),
    )


def project_access_response(project: BlogProject, membership: ProjectMembership) -> ProjectAccessResponse:
    return ProjectAccessResponse(project=project_response(project), membership=membership_response(membership))


def workspace_response(snapshot: WorkspaceSnapshot) -> WorkspaceResponse:
    return WorkspaceResponse(
        projectId=snapshot.project_id,
        workspace=snapshot.payload,
        createdAt=_dt(snapshot.created_at),
    )


def project_response(project: BlogProject) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        ownerUserId=project.owner_user_id,
        title=project.title,
        description=project.description,
        language=project.language,
        status=project.status,
        benchmarkRole=project.benchmark_role,
        createdAt=_dt(project.created_at),
        updatedAt=_dt(project.updated_at),
    )


def membership_response(membership: ProjectMembership) -> MembershipResponse:
    return MembershipResponse(
        id=membership.id,
        userId=membership.user_id,
        projectId=membership.project_id,
        role=membership.role,
        status=membership.status,
    )


def _dt(value: Any) -> str:
    return value.isoformat().replace("+00:00", "Z")
