"""User repository port."""
from typing import Protocol, Optional

from app.domain.models.user import User
from app.domain.models.value_objects import UserId


class UserRepository(Protocol):
    """Repository interface for User entities."""

    def save(self, user: User) -> None:
        """Persist a user."""
        ...

    def find_by_id(self, user_id: UserId) -> Optional[User]:
        """Find user by ID."""
        ...

    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        ...
