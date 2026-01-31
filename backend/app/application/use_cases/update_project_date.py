"""UC-062: Update Project Date use case."""
from app.application.dtos.schedule_dtos import UpdateProjectDateInput
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.project_schedule_history import ProjectScheduleHistory


class UpdateProjectDateUseCase:
    """Use case for updating project date (UC-062)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, input_dto: UpdateProjectDateInput) -> None:
        """Update project expected end date."""
        with self.uow:
            project = self.uow.projects.find_by_id(input_dto.project_id)
            if project is None:
                raise BusinessRuleViolation("Project not found", code="project_not_found")

            previous_end = project.expected_end_date
            project.expected_end_date = input_dto.new_end_date
            self.uow.projects.save(project)

            if previous_end is not None:
                history = ProjectScheduleHistory.create(
                    project_id=project.id,
                    previous_end=previous_end,
                    new_end=input_dto.new_end_date,
                    reason=input_dto.reason,
                )
                self.uow.schedule_history.save_project_history(history)

            self.uow.commit()
