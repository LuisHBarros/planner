"""Role repository port."""
from typing import Protocol, Optional, List
from uuid import UUID
from app.domain.models.role import Role


class RoleRepository(Protocol):
    """Repository interface for Role entities."""
    
    def save(self, role: Role) -> None:
        """Save a role."""
        ...
    
    def find_by_id(self, role_id: UUID) -> Optional[Role]:
        """Find role by ID."""
        ...
    
    def find_by_team_id(self, team_id: UUID) -> List[Role]:
        """Find all roles for a team."""
        ...
    
    def find_by_user_and_team(self, user_id: UUID, team_id: UUID) -> List[Role]:
        """Find all roles for a user in a team."""
        ...
