"""UC: List teams for current user (Spec 3.0 /me/teams)."""
from uuid import UUID
from typing import List

from app.domain.models.team import Team
from app.application.ports.team_member_repository import TeamMemberRepository
from app.application.ports.team_repository import TeamRepository


class GetUserTeamsUseCase:
    """Use case for listing teams that a user belongs to."""

    def __init__(
        self,
        team_member_repository: TeamMemberRepository,
        team_repository: TeamRepository,
    ) -> None:
        self.team_member_repository = team_member_repository
        self.team_repository = team_repository

    def execute(self, user_id: UUID) -> List[Team]:
        """Return all teams the given user is a member of."""
        memberships = self.team_member_repository.find_by_user_id(user_id)
        team_ids = {m.team_id for m in memberships}
        teams: List[Team] = []
        for team_id in team_ids:
            team = self.team_repository.find_by_id(team_id)
            if team is not None:
                teams.append(team)
        return teams

