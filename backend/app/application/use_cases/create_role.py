"""UC-012: Create Role use case."""
from app.application.dtos.project_dtos import CreateRoleInput, RoleOutput
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.role import Role


class CreateRoleUseCase:
    """Use case for creating a role (UC-012)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, input_dto: CreateRoleInput) -> RoleOutput:
        """Create a role."""
        with self.uow:
            project = self.uow.projects.find_by_id(input_dto.project_id)
            if project is None:
                raise BusinessRuleViolation("Project not found", code="project_not_found")

            role = Role.create(
                project_id=input_dto.project_id,
                name=input_dto.name,
                description=input_dto.description,
            )
            self.uow.roles.save(role)
            self.uow.commit()
            return RoleOutput.from_domain(role)
