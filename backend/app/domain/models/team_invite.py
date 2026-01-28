"""TeamInvite domain model for token-based team invitations (Spec 3.0)."""
from datetime import datetime, UTC, timedelta
from typing import Optional
from uuid import UUID, uuid4

from app.domain.models.enums import TeamMemberRole


class TeamInvite:
    """Invitation to join a team via token link."""

    def __init__(
        self,
        id: UUID,
        team_id: UUID,
        role: TeamMemberRole,
        token: str,
        expires_at: datetime,
        created_by: UUID,
        created_at: datetime,
        used_at: Optional[datetime] = None,
    ) -> None:
        self.id = id
        self.team_id = team_id
        self.role = role
        self.token = token
        self.expires_at = expires_at
        self.created_by = created_by
        self.created_at = created_at
        self.used_at = used_at

    @classmethod
    def create(
        cls,
        team_id: UUID,
        role: TeamMemberRole,
        created_by: UUID,
        expires_at: Optional[datetime] = None,
        token: Optional[str] = None,
    ) -> "TeamInvite":
        """Create a new invite with a token and expiry."""
        now = datetime.now(UTC)
        if expires_at is None:
            expires_at = now + timedelta(days=7)

        return cls(
            id=uuid4(),
            team_id=team_id,
            role=role,
            token=token or uuid4().hex,
            expires_at=expires_at,
            created_by=created_by,
            created_at=now,
            used_at=None,
        )

    def mark_used(self) -> None:
        """Mark this invite as used."""
        self.used_at = datetime.now(UTC)

    def is_valid(self, now: Optional[datetime] = None) -> bool:
        """Return True if invite is not expired and not yet used."""
        if now is None:
            now = datetime.now(UTC)
        if self.used_at is not None:
            return False
        return now <= self.expires_at

