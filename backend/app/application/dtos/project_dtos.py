"""Project-related DTOs."""
from dataclasses import dataclass
from typing import Optional

from app.domain.models.project import Project
from app.domain.models.project_invite import ProjectInvite
from app.domain.models.project_member import ProjectMember
from app.domain.models.role import Role
from app.domain.models.value_objects import (
    InviteToken,
    ProjectId,
    ProjectInviteId,
    ProjectMemberId,
    RoleId,
    UserId,
    UtcDateTime,
)
from app.domain.models.enums import InviteStatus, MemberLevel, ProjectStatus


@dataclass(frozen=True)
class CreateProjectInput:
    """Input for creating a project."""
    name: str
    created_by: UserId
    description: Optional[str] = None
    expected_end_date: Optional[UtcDateTime] = None


@dataclass(frozen=True)
class ProjectOutput:
    """Project output DTO."""
    id: ProjectId
    name: str
    description: Optional[str]
    created_by: UserId
    expected_end_date: Optional[UtcDateTime]
    status: ProjectStatus

    @staticmethod
    def from_domain(project: Project) -> "ProjectOutput":
        """Create output DTO from domain model."""
        return ProjectOutput(
            id=project.id,
            name=project.name,
            description=project.description,
            created_by=project.created_by,
            expected_end_date=project.expected_end_date,
            status=project.status,
        )


@dataclass(frozen=True)
class ConfigureProjectLlmInput:
    """Input for configuring project LLM."""
    project_id: ProjectId
    provider: str
    api_key_encrypted: str


@dataclass(frozen=True)
class CreateRoleInput:
    """Input for creating a role."""
    project_id: ProjectId
    name: str
    description: Optional[str] = None


@dataclass(frozen=True)
class RoleOutput:
    """Role output DTO."""
    id: RoleId
    project_id: ProjectId
    name: str
    description: Optional[str]

    @staticmethod
    def from_domain(role: Role) -> "RoleOutput":
        """Create output DTO from domain model."""
        return RoleOutput(
            id=role.id,
            project_id=role.project_id,
            name=role.name,
            description=role.description,
        )


@dataclass(frozen=True)
class CreateProjectInviteInput:
    """Input for creating a project invite."""
    project_id: ProjectId
    email: str
    token: InviteToken | None = None
    role_id: Optional[RoleId] = None
    expires_at: Optional[UtcDateTime] = None


@dataclass(frozen=True)
class AcceptInviteInput:
    """Input for accepting a project invite."""
    token: InviteToken
    user_id: UserId
    level: MemberLevel
    base_capacity: int


@dataclass(frozen=True)
class ProjectInviteOutput:
    """Project invite output DTO."""
    id: ProjectInviteId
    project_id: ProjectId
    email: str
    token: InviteToken
    role_id: Optional[RoleId]
    status: InviteStatus
    expires_at: Optional[UtcDateTime]

    @staticmethod
    def from_domain(invite: ProjectInvite) -> "ProjectInviteOutput":
        """Create output DTO from domain model."""
        return ProjectInviteOutput(
            id=invite.id,
            project_id=invite.project_id,
            email=invite.email,
            token=invite.token,
            role_id=invite.role_id,
            status=invite.status,
            expires_at=invite.expires_at,
        )


@dataclass(frozen=True)
class ProjectMemberOutput:
    """Project member output DTO."""
    id: ProjectMemberId
    project_id: ProjectId
    user_id: UserId
    role_id: Optional[RoleId]
    level: MemberLevel
    base_capacity: int
    is_manager: bool

    @staticmethod
    def from_domain(member: ProjectMember) -> "ProjectMemberOutput":
        """Create output DTO from domain model."""
        return ProjectMemberOutput(
            id=member.id,
            project_id=member.project_id,
            user_id=member.user_id,
            role_id=member.role_id,
            level=member.level,
            base_capacity=member.base_capacity,
            is_manager=member.is_manager,
        )
