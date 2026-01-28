"""UC-Invitation: Accept Team Invite use case (Spec 3.0)."""
from uuid import UUID

from app.domain.models.team_member import TeamMember
from app.application.ports.team_invite_repository import TeamInviteRepository
from app.application.ports.team_member_repository import TeamMemberRepository
from app.application.ports.user_repository import UserRepository
from app.application.ports.team_repository import TeamRepository
from app.domain.exceptions import BusinessRuleViolation


class AcceptTeamInviteUseCase:
    """Use case for accepting a team invite by token."""

    def __init__(
        self,
        invite_repository: TeamInviteRepository,
        member_repository: TeamMemberRepository,
        user_repository: UserRepository,
        team_repository: TeamRepository,
    ) -> None:
        self.invite_repository = invite_repository
        self.member_repository = member_repository
        self.user_repository = user_repository
        self.team_repository = team_repository

    def execute(self, token: str, user_id: UUID) -> TeamMember:
        """
        Accept an invite using its token.

        Flow:
        1. Load invite by token
        2. Validate not expired / not used
        3. Validate user and team exist
        4. Create TeamMember with invite.role
        5. Mark invite as used
        6. Persist both and return membership
        """
        invite = self.invite_repository.find_by_token(token)
        if invite is None:
            raise BusinessRuleViolation("Invite not found", code="invite_not_found")

        if not invite.is_valid():
            raise BusinessRuleViolation("Invite expired or already used", code="invite_invalid")

        user = self.user_repository.find_by_id(user_id)
        if user is None:
            raise BusinessRuleViolation(
                f"User with id {user_id} not found",
                code="user_not_found",
            )

        team = self.team_repository.find_by_id(invite.team_id)
        if team is None:
            raise BusinessRuleViolation(
                f"Team with id {invite.team_id} not found",
                code="team_not_found",
            )

        member = TeamMember.join(
            user_id=user.id,
            team_id=invite.team_id,
            role=invite.role,
        )
        self.member_repository.save(member)

        invite.mark_used()
        self.invite_repository.save(invite)

        return member

