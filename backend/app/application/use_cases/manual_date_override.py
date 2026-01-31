"""UC-064: Manual Date Override use case."""
from app.application.dtos.schedule_dtos import ManualDateOverrideInput
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import ScheduleChangeReason
from app.domain.models.task_schedule_history import TaskScheduleHistory


class ManualDateOverrideUseCase:
    """Use case for manually overriding task dates (UC-064)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, input_dto: ManualDateOverrideInput) -> None:
        """Manually override task expected dates."""
        with self.uow:
            task = self.uow.tasks.find_by_id(input_dto.task_id)
            if task is None:
                raise BusinessRuleViolation("Task not found", code="task_not_found")

            previous_start = task.expected_start_date
            previous_end = task.expected_end_date
            task.expected_start_date = input_dto.new_start_date
            task.expected_end_date = input_dto.new_end_date
            self.uow.tasks.save(task)

            if previous_start and previous_end:
                history = TaskScheduleHistory.create(
                    task_id=task.id,
                    previous_start=previous_start,
                    previous_end=previous_end,
                    new_start=input_dto.new_start_date,
                    new_end=input_dto.new_end_date,
                    reason=ScheduleChangeReason.MANUAL_OVERRIDE,
                )
                self.uow.schedule_history.save_task_history(history)

            self.uow.commit()
