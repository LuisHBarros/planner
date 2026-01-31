"""UC-042: Add Task Report use case."""
from app.application.dtos.task_dtos import TaskReportInput, TaskReportOutput
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.models.task_report import TaskReport


class AddTaskReportUseCase:
    """Use case for adding a task report (UC-042)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, input_dto: TaskReportInput) -> TaskReportOutput:
        """Add a task progress report."""
        with self.uow:
            report = TaskReport.create(
                task_id=input_dto.task_id,
                author_id=input_dto.author_id,
                progress=input_dto.progress,
                source=input_dto.source,
                note=input_dto.note,
            )
            self.uow.task_reports.save(report)
            self.uow.commit()
            return TaskReportOutput.from_domain(report)
