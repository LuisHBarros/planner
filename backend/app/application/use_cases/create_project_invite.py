"""UC-020: Create Project Invite use case."""
from uuid import uuid4

from app.application.dtos.project_dtos import CreateProjectInviteInput, ProjectInviteOutput
from app.application.events.domain_events import ProjectInviteCreated
from app.application.ports.event_bus import EventBus
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.project_invite import ProjectInvite
from app.domain.models.value_objects import InviteToken


class CreateProjectInviteUseCase:
    """Use case for creating a project invite (UC-020)."""

    def __init__(self, uow: UnitOfWork, event_bus: EventBus):
        self.uow = uow
        self.event_bus = event_bus

    def execute(self, input_dto: CreateProjectInviteInput) -> ProjectInviteOutput:
        """Create a project invite."""
        with self.uow:
            project = self.uow.projects.find_by_id(input_dto.project_id)
            if project is None:
                raise BusinessRuleViolation("Project not found", code="project_not_found")

            token = input_dto.token or InviteToken(str(uuid4()))
            invite = ProjectInvite.create(
                project_id=input_dto.project_id,
                email=input_dto.email,
                token=token,
                role_id=input_dto.role_id,
                expires_at=input_dto.expires_at.value if input_dto.expires_at else None,
            )
            self.uow.project_invites.save(invite)
            self.uow.commit()

            self.event_bus.emit(ProjectInviteCreated(
                invite_id=invite.id,
                project_id=invite.project_id,
                email=invite.email,
            ))

            return ProjectInviteOutput.from_domain(invite)
