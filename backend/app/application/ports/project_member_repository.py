"""ProjectMember repository port."""
from typing import Protocol, Optional, List

from app.domain.models.project_member import ProjectMember
from app.domain.models.value_objects import ProjectId, ProjectMemberId, UserId


class ProjectMemberRepository(Protocol):
    """Repository interface for ProjectMember entities."""

    def save(self, member: ProjectMember) -> None:
        """Persist a project member."""
        ...

    def find_by_id(self, member_id: ProjectMemberId) -> Optional[ProjectMember]:
        """Find project member by ID."""
        ...

    def list_by_project(self, project_id: ProjectId) -> List[ProjectMember]:
        """List members in a project."""
        ...

    def find_by_project_and_user(
        self,
        project_id: ProjectId,
        user_id: UserId,
    ) -> Optional[ProjectMember]:
        """Find a member by project and user."""
        ...
