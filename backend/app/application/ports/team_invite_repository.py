"""Team invite repository port."""
from typing import Protocol, Optional

from app.domain.models.team_invite import TeamInvite


class TeamInviteRepository(Protocol):
    """Repository interface for TeamInvite entities."""

    def save(self, invite: TeamInvite) -> None:
        """Persist an invite (idempotent upsert)."""
        ...

    def find_by_token(self, token: str) -> Optional[TeamInvite]:
        """Find invite by public token."""
        ...

