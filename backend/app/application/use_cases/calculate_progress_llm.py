"""UC-043: Calculate Task Progress (LLM) use case."""
from app.application.dtos.task_dtos import CalculateProgressInput, TaskReportOutput
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import ProgressSource
from app.domain.models.task_report import TaskReport


class CalculateProgressLlmUseCase:
    """Use case for calculating task progress via LLM (UC-043)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, input_dto: CalculateProgressInput) -> TaskReportOutput:
        """Calculate progress and store report."""
        with self.uow:
            task = self.uow.tasks.find_by_id(input_dto.task_id)
            if task is None:
                raise BusinessRuleViolation("Task not found", code="task_not_found")

            progress = self.uow.llm_service.calculate_task_progress(task)
            report = TaskReport.create(
                task_id=task.id,
                author_id=input_dto.author_id,
                progress=progress,
                source=ProgressSource.LLM,
            )
            self.uow.task_reports.save(report)
            self.uow.commit()
            return TaskReportOutput.from_domain(report)
