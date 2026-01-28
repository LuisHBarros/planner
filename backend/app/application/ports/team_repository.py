"""Team repository port."""
from typing import Protocol, Optional, List
from uuid import UUID
from app.domain.models.team import Team


class TeamRepository(Protocol):
    """Repository interface for Team entities."""
    
    def save(self, team: Team) -> None:
        """Save a team."""
        ...
    
    def find_by_id(self, team_id: UUID) -> Optional[Team]:
        """Find team by ID."""
        ...
    
    def find_by_company_id(self, company_id: UUID) -> List[Team]:
        """Find all teams for a company."""
        ...
