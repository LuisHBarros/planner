"""UC-061: Propagate Schedule use case."""
from datetime import timedelta

from app.application.dtos.schedule_dtos import PropagateScheduleInput
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import ScheduleChangeReason
from app.domain.models.task_schedule_history import TaskScheduleHistory
from app.domain.services.schedule_calculator import calculate_new_dates


class PropagateScheduleUseCase:
    """Use case for schedule propagation (UC-061)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, input_dto: PropagateScheduleInput) -> None:
        """Propagate schedule changes for a task."""
        with self.uow:
            task = self.uow.tasks.find_by_id(input_dto.task_id)
            if task is None:
                raise BusinessRuleViolation("Task not found", code="task_not_found")

            delay_delta = timedelta(seconds=input_dto.delay_delta_seconds)
            previous_start = task.expected_start_date
            previous_end = task.expected_end_date

            new_start, new_end = calculate_new_dates(task, delay_delta)
            task.expected_start_date = new_start
            task.expected_end_date = new_end
            self.uow.tasks.save(task)

            if previous_start and previous_end and new_start and new_end:
                history = TaskScheduleHistory.create(
                    task_id=task.id,
                    previous_start=previous_start,
                    previous_end=previous_end,
                    new_start=new_start,
                    new_end=new_end,
                    reason=ScheduleChangeReason.DEPENDENCY_DELAY,
                )
                self.uow.schedule_history.save_task_history(history)

            self.uow.commit()
