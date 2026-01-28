"""UC-004: Create Project use case."""
from uuid import UUID
from typing import Optional

from app.domain.models.project import Project
from app.application.ports.project_repository import ProjectRepository
from app.application.ports.team_repository import TeamRepository
from app.domain.exceptions import BusinessRuleViolation


class CreateProjectUseCase:
    """Use case for creating a project (UC-004)."""
    
    def __init__(
        self,
        project_repository: ProjectRepository,
        team_repository: TeamRepository,
    ):
        self.project_repository = project_repository
        self.team_repository = team_repository
    
    def execute(
        self,
        team_id: UUID,
        name: str,
        description: Optional[str] = None,
    ) -> Project:
        """
        Create a new project.
        
        Flow:
        1. Validate team exists
        2. Create project
        3. Return project details
        """
        # Validate team exists
        team = self.team_repository.find_by_id(team_id)
        if team is None:
            raise BusinessRuleViolation(
                f"Team with id {team_id} not found",
                code="team_not_found"
            )
        
        # Create project
        project = Project.create(
            team_id=team_id,
            name=name,
            description=description,
        )
        
        # Save
        self.project_repository.save(project)
        
        return project
