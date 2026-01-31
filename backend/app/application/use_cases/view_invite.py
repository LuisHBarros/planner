"""UC-021: View Invite use case."""
from app.application.dtos.project_dtos import ProjectInviteOutput
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.value_objects import InviteToken


class ViewInviteUseCase:
    """Use case for viewing an invite (UC-021)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, token: InviteToken) -> ProjectInviteOutput:
        """View an invite by token."""
        with self.uow:
            invite = self.uow.project_invites.find_by_token(token)
            if invite is None:
                raise BusinessRuleViolation("Invite not found", code="invite_not_found")
            return ProjectInviteOutput.from_domain(invite)
