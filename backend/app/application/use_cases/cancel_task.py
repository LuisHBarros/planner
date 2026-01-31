"""UC-035: Cancel Task use case."""
from app.application.dtos.task_dtos import TaskOutput
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import TaskStatus
from app.domain.models.value_objects import TaskId


class CancelTaskUseCase:
    """Use case for cancelling a task (UC-035)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, task_id: TaskId) -> TaskOutput:
        """Cancel a task."""
        with self.uow:
            task = self.uow.tasks.find_by_id(task_id)
            if task is None:
                raise BusinessRuleViolation("Task not found", code="task_not_found")

            task.transition_to(TaskStatus.CANCELLED)
            task.assigned_to = None
            self.uow.tasks.save(task)
            self.uow.commit()
            return TaskOutput.from_domain(task)
