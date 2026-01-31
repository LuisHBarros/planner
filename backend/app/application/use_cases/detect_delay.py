"""UC-060: Detect Delay use case."""
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.value_objects import TaskId
from app.domain.services.schedule_calculator import detect_delay


class DetectDelayUseCase:
    """Use case for detecting delay (UC-060)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, task_id: TaskId) -> bool:
        """Detect if a task is delayed."""
        with self.uow:
            task = self.uow.tasks.find_by_id(task_id)
            if task is None:
                raise BusinessRuleViolation("Task not found", code="task_not_found")
            return detect_delay(task)
