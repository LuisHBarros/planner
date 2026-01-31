"""UC-044: Update Task Progress (manual) use case."""
from app.application.dtos.task_dtos import TaskReportInput, TaskReportOutput
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.models.enums import ProgressSource
from app.domain.models.task_report import TaskReport


class UpdateProgressManualUseCase:
    """Use case for updating task progress manually (UC-044)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, input_dto: TaskReportInput) -> TaskReportOutput:
        """Store a manual progress report."""
        with self.uow:
            report = TaskReport.create(
                task_id=input_dto.task_id,
                author_id=input_dto.author_id,
                progress=input_dto.progress,
                source=ProgressSource.MANUAL,
                note=input_dto.note,
            )
            self.uow.task_reports.save(report)
            self.uow.commit()
            return TaskReportOutput.from_domain(report)
