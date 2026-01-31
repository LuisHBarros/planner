"""UC-013: Get Project use case."""
from app.application.dtos.project_dtos import ProjectOutput
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.value_objects import ProjectId


class GetProjectUseCase:
    """Use case for fetching a project (UC-013)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, project_id: ProjectId) -> ProjectOutput:
        """Get a project by ID."""
        with self.uow:
            project = self.uow.projects.find_by_id(project_id)
            if project is None:
                raise BusinessRuleViolation("Project not found", code="project_not_found")
            return ProjectOutput.from_domain(project)
