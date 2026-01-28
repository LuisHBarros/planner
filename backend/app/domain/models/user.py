"""User domain model."""
from datetime import datetime, UTC
from typing import Optional
from uuid import UUID, uuid4


class User:
    """User entity."""

    def __init__(
        self,
        id: UUID,
        email: str,
        name: str,
        preferred_language: Optional[str] = None,
        avatar_url: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.email = email
        self.name = name
        self.preferred_language = preferred_language
        self.avatar_url = avatar_url
        self.created_at = created_at or datetime.now(UTC)

    @classmethod
    def create(
        cls,
        email: str,
        name: str,
        preferred_language: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> "User":
        """Create a new user."""
        return cls(
            id=uuid4(),
            email=email,
            name=name,
            preferred_language=preferred_language,
            avatar_url=avatar_url,
        )
