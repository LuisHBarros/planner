"""Role repository port."""
from typing import Protocol, Optional, List

from app.domain.models.role import Role
from app.domain.models.value_objects import ProjectId, RoleId


class RoleRepository(Protocol):
    """Repository interface for Role entities."""

    def save(self, role: Role) -> None:
        """Persist a role."""
        ...

    def find_by_id(self, role_id: RoleId) -> Optional[Role]:
        """Find role by ID."""
        ...

    def list_by_project(self, project_id: ProjectId) -> List[Role]:
        """List roles in a project."""
        ...
