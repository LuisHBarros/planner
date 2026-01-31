"""User domain model per BUSINESS_RULES.md."""
from dataclasses import dataclass, field

from app.domain.models.value_objects import UserId, UtcDateTime


@dataclass
class User:
    """User entity - registered via magic link."""
    id: UserId
    email: str
    name: str
    created_at: UtcDateTime = field(default_factory=UtcDateTime.now)

    @classmethod
    def create(cls, email: str, name: str) -> "User":
        """Create a new user (BR-AUTH-003: email unique, case-insensitive)."""
        return cls(
            id=UserId(),
            email=email.lower().strip(),
            name=name.strip(),
        )
