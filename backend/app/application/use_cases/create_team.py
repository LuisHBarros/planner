"""UC-001: Create Team use case."""
from uuid import UUID
from typing import Optional

from app.domain.models.team import Team
from app.application.ports.team_repository import TeamRepository
from app.application.ports.company_repository import CompanyRepository
from app.domain.exceptions import BusinessRuleViolation


class CreateTeamUseCase:
    """Use case for creating a team (UC-001)."""
    
    def __init__(
        self,
        team_repository: TeamRepository,
        company_repository: CompanyRepository,
    ):
        self.team_repository = team_repository
        self.company_repository = company_repository
    
    def execute(
        self,
        company_id: UUID,
        name: str,
        description: Optional[str] = None,
        default_language: str = "en",
    ) -> Team:
        """
        Create a new team.
        
        Flow:
        1. Validate company exists
        2. Create team
        3. Return team details
        """
        # Validate company exists
        company = self.company_repository.find_by_id(company_id)
        if company is None:
            raise BusinessRuleViolation(
                f"Company with id {company_id} not found",
                code="company_not_found"
            )
        
        # Create team
        team = Team.create(
            company_id=company_id,
            name=name,
            description=description,
            default_language=default_language,
        )
        
        # Save
        self.team_repository.save(team)
        
        return team
