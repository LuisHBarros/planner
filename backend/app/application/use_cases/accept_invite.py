"""UC-022: Accept Project Invite use case."""
from app.application.dtos.project_dtos import AcceptInviteInput, ProjectInviteOutput
from app.application.events.domain_events import ProjectInviteAccepted
from app.application.ports.event_bus import EventBus
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.project_member import ProjectMember


class AcceptInviteUseCase:
    """Use case for accepting a project invite (UC-022)."""

    def __init__(self, uow: UnitOfWork, event_bus: EventBus):
        self.uow = uow
        self.event_bus = event_bus

    def execute(self, input_dto: AcceptInviteInput) -> ProjectInviteOutput:
        """Accept an invite and create project membership."""
        with self.uow:
            invite = self.uow.project_invites.find_by_token(input_dto.token)
            if invite is None:
                raise BusinessRuleViolation("Invite not found", code="invite_not_found")

            invite.accept()
            self.uow.project_invites.save(invite)

            member = ProjectMember.create_member(
                project_id=invite.project_id,
                user_id=input_dto.user_id,
                level=input_dto.level,
                base_capacity=input_dto.base_capacity,
                role_id=invite.role_id,
            )
            self.uow.project_members.save(member)

            self.uow.commit()

            self.event_bus.emit(ProjectInviteAccepted(
                invite_id=invite.id,
                project_id=invite.project_id,
                user_id=input_dto.user_id,
            ))

            return ProjectInviteOutput.from_domain(invite)
