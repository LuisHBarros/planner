"""User repository port."""
from typing import Protocol, Optional, List
from uuid import UUID
from app.domain.models.user import User


class UserRepository(Protocol):
    """Repository interface for User entities."""
    
    def save(self, user: User) -> None:
        """Save a user."""
        ...
    
    def find_by_id(self, user_id: UUID) -> Optional[User]:
        """Find user by ID."""
        ...
    
    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        ...
    
    def find_by_team_id(self, team_id: UUID) -> List[User]:
        """Find all users in a team."""
        ...
