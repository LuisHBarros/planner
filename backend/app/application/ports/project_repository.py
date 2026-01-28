"""Project repository port."""
from typing import Protocol, Optional, List
from uuid import UUID
from app.domain.models.project import Project


class ProjectRepository(Protocol):
    """Repository interface for Project entities."""
    
    def save(self, project: Project) -> None:
        """Save a project."""
        ...
    
    def find_by_id(self, project_id: UUID) -> Optional[Project]:
        """Find project by ID."""
        ...
    
    def find_by_team_id(self, team_id: UUID) -> List[Project]:
        """Find all projects for a team."""
        ...
