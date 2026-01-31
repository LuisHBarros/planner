"""Project repository port."""
from typing import Protocol, Optional, List

from app.domain.models.project import Project
from app.domain.models.value_objects import ProjectId, UserId


class ProjectRepository(Protocol):
    """Repository interface for Project entities."""

    def save(self, project: Project) -> None:
        """Persist a project."""
        ...

    def find_by_id(self, project_id: ProjectId) -> Optional[Project]:
        """Find project by ID."""
        ...

    def find_by_created_by(self, user_id: UserId) -> List[Project]:
        """Find all projects created by a user."""
        ...

    def delete(self, project_id: ProjectId) -> None:
        """Delete a project."""
        ...
