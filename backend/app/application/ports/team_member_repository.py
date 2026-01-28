"""Team member repository port."""
from typing import Protocol, List
from uuid import UUID

from app.domain.models.team_member import TeamMember


class TeamMemberRepository(Protocol):
    """Repository interface for TeamMember entities."""

    def save(self, member: TeamMember) -> None:
        """Persist a team membership."""
        ...

    def find_by_user_id(self, user_id: UUID) -> List[TeamMember]:
        """Find all team memberships for a user."""
        ...

    def find_by_team_id(self, team_id: UUID) -> List[TeamMember]:
        """Find all memberships for a team."""
        ...

