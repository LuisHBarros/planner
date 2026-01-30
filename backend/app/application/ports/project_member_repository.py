"""Port for ProjectMember repository (v3.0)."""
from typing import List, Optional, Protocol
from uuid import UUID

from app.domain.models.project_member import ProjectMember


class ProjectMemberRepository(Protocol):
    """Repository interface for ProjectMember entities."""

    def save(self, project_member: ProjectMember) -> None:
        """Persist a project member."""
        ...

    def find_by_id(self, project_member_id: UUID) -> Optional[ProjectMember]:
        """Find a project member by ID."""
        ...

    def find_by_project_id(self, project_id: UUID) -> List[ProjectMember]:
        """Find all members of a project."""
        ...

    def find_by_user_id(self, user_id: UUID) -> List[ProjectMember]:
        """Find all project memberships for a user."""
        ...

    def find_by_project_and_user(
        self, project_id: UUID, user_id: UUID
    ) -> Optional[ProjectMember]:
        """Find a specific user's membership in a project."""
        ...

    def find_active_by_project_id(self, project_id: UUID) -> List[ProjectMember]:
        """Find all active members of a project."""
        ...

    def delete(self, project_member_id: UUID) -> None:
        """Delete a project member."""
        ...
