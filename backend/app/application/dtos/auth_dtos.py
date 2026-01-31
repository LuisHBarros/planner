"""Authentication DTOs."""
from dataclasses import dataclass

from app.domain.models.user import User
from app.domain.models.value_objects import InviteToken, UserId, UtcDateTime


@dataclass(frozen=True)
class RegisterUserInput:
    """Input for user registration."""
    email: str
    name: str


@dataclass(frozen=True)
class LoginUserInput:
    """Input for login (magic link request)."""
    email: str
    expires_at: UtcDateTime
    token: InviteToken | None = None


@dataclass(frozen=True)
class VerifyMagicLinkInput:
    """Input for magic link verification."""
    token: InviteToken


@dataclass(frozen=True)
class UserOutput:
    """User output DTO."""
    id: UserId
    email: str
    name: str
    created_at: UtcDateTime

    @staticmethod
    def from_domain(user: User) -> "UserOutput":
        """Create output DTO from domain model."""
        return UserOutput(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
        )


@dataclass(frozen=True)
class MagicLinkOutput:
    """Magic link output DTO."""
    token: InviteToken
    expires_at: UtcDateTime
