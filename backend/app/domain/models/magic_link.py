"""MagicLink domain model."""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.value_objects import InviteToken, MagicLinkId, UserId, UtcDateTime


@dataclass
class MagicLink:
    """Magic link for authentication."""
    id: MagicLinkId
    token: InviteToken
    user_id: UserId
    expires_at: UtcDateTime
    consumed_at: Optional[UtcDateTime]

    @classmethod
    def create(
        cls,
        token: InviteToken,
        user_id: UserId,
        expires_at: UtcDateTime,
    ) -> "MagicLink":
        """Create a magic link."""
        return cls(
            id=MagicLinkId(),
            token=token,
            user_id=user_id,
            expires_at=expires_at,
            consumed_at=None,
        )

    def is_expired(self) -> bool:
        """Check whether the link has expired."""
        return self.expires_at.value < datetime.now(timezone.utc)

    def consume(self) -> None:
        """Mark link as used if valid."""
        if self.is_expired():
            raise BusinessRuleViolation("Magic link expired", code="magic_link_expired")
        if self.consumed_at is not None:
            raise BusinessRuleViolation("Magic link already used", code="magic_link_used")
        self.consumed_at = UtcDateTime.now()
