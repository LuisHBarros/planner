"""TeamMember domain model representing membership of a user in a team."""
from datetime import datetime, UTC
from uuid import UUID, uuid4

from app.domain.models.enums import TeamMemberRole


class TeamMember:
    """Team membership with a role within the team (Spec 3.0)."""

    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        team_id: UUID,
        role: TeamMemberRole,
        joined_at: datetime,
    ) -> None:
        self.id = id
        self.user_id = user_id
        self.team_id = team_id
        self.role = role
        self.joined_at = joined_at

    @classmethod
    def join(
        cls,
        user_id: UUID,
        team_id: UUID,
        role: TeamMemberRole,
    ) -> "TeamMember":
        """Create a new TeamMember on successful invite acceptance."""
        return cls(
            id=uuid4(),
            user_id=user_id,
            team_id=team_id,
            role=role,
            joined_at=datetime.now(UTC),
        )

