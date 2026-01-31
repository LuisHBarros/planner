"""UC-010: Create Project use case."""
from app.application.dtos.project_dtos import CreateProjectInput, ProjectOutput
from app.application.events.domain_events import ProjectCreated
from app.application.ports.event_bus import EventBus
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.project import Project
from app.domain.models.project_member import ProjectMember


class CreateProjectUseCase:
    """Use case for creating a project (UC-010, BR-PROJ-001)."""

    def __init__(self, uow: UnitOfWork, event_bus: EventBus):
        self.uow = uow
        self.event_bus = event_bus

    def execute(self, input_dto: CreateProjectInput) -> ProjectOutput:
        """Create a new project."""
        with self.uow:
            user = self.uow.users.find_by_id(input_dto.created_by)
            if user is None:
                raise BusinessRuleViolation(
                    f"User with id {input_dto.created_by} not found",
                    code="user_not_found",
                )

            project = Project.create(
                name=input_dto.name,
                created_by=input_dto.created_by,
                expected_end_date=input_dto.expected_end_date,
                description=input_dto.description,
            )
            self.uow.projects.save(project)

            manager_member = ProjectMember.create_manager(
                project_id=project.id,
                user_id=input_dto.created_by,
            )
            self.uow.project_members.save(manager_member)

            self.uow.commit()

            self.event_bus.emit(ProjectCreated(
                project_id=project.id,
                created_by=input_dto.created_by,
                name=project.name,
            ))

            return ProjectOutput.from_domain(project)
