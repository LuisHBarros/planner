"""UC-Invitation: Create Team Invite use case (Spec 3.0)."""
from datetime import datetime, UTC
from typing import Optional
from uuid import UUID

from app.domain.models.team_invite import TeamInvite
from app.domain.models.enums import TeamMemberRole
from app.application.ports.team_repository import TeamRepository
from app.application.ports.team_invite_repository import TeamInviteRepository
from app.domain.exceptions import BusinessRuleViolation


class CreateTeamInviteUseCase:
    """Use case for creating a token-based team invite."""

    def __init__(
        self,
        team_repository: TeamRepository,
        invite_repository: TeamInviteRepository,
    ) -> None:
        self.team_repository = team_repository
        self.invite_repository = invite_repository

    def execute(
        self,
        team_id: UUID,
        role: TeamMemberRole,
        created_by: UUID,
        expires_at: Optional[datetime] = None,
    ) -> TeamInvite:
        """
        Create an invite link for a team.

        Flow:
        1. Validate team exists
        2. Create invite with token and expiry
        3. Persist and return invite
        """
        team = self.team_repository.find_by_id(team_id)
        if team is None:
            raise BusinessRuleViolation(
                f"Team with id {team_id} not found",
                code="team_not_found",
            )

        invite = TeamInvite.create(
            team_id=team_id,
            role=role,
            created_by=created_by,
            expires_at=expires_at,
        )
        self.invite_repository.save(invite)
        return invite

