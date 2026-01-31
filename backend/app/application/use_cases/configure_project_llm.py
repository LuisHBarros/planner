"""UC-011: Configure Project LLM use case."""
from app.application.dtos.project_dtos import ConfigureProjectLlmInput, ProjectOutput
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation


class ConfigureProjectLlmUseCase:
    """Use case for configuring LLM settings (UC-011)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, input_dto: ConfigureProjectLlmInput) -> ProjectOutput:
        """Enable LLM for a project."""
        with self.uow:
            project = self.uow.projects.find_by_id(input_dto.project_id)
            if project is None:
                raise BusinessRuleViolation("Project not found", code="project_not_found")

            project.enable_llm(input_dto.provider, input_dto.api_key_encrypted)
            self.uow.projects.save(project)
            self.uow.commit()

            return ProjectOutput.from_domain(project)
