"""ProjectMember domain model."""
from dataclasses import dataclass, field

from app.domain.models.enums import MemberLevel
from app.domain.models.value_objects import ProjectId, ProjectMemberId, UserId, RoleId, UtcDateTime


@dataclass
class ProjectMember:
    """User membership within a project."""
    id: ProjectMemberId
    project_id: ProjectId
    user_id: UserId
    role_id: RoleId | None
    level: MemberLevel
    base_capacity: int
    is_manager: bool
    joined_at: UtcDateTime = field(default_factory=UtcDateTime.now)

    @classmethod
    def create_member(
        cls,
        project_id: ProjectId,
        user_id: UserId,
        level: MemberLevel,
        base_capacity: int,
        role_id: RoleId | None = None,
    ) -> "ProjectMember":
        """Create a non-manager project member."""
        return cls(
            id=ProjectMemberId(),
            project_id=project_id,
            user_id=user_id,
            role_id=role_id,
            level=level,
            base_capacity=base_capacity,
            is_manager=False,
        )

    @classmethod
    def create_manager(
        cls,
        project_id: ProjectId,
        user_id: UserId,
    ) -> "ProjectMember":
        """Create a manager project member."""
        return cls(
            id=ProjectMemberId(),
            project_id=project_id,
            user_id=user_id,
            role_id=None,
            level=MemberLevel.LEAD,
            base_capacity=0,
            is_manager=True,
        )
