"""UC-045: Complete Task use case."""
from app.application.dtos.task_dtos import TaskOutput
from app.application.events.domain_events import TaskCompleted
from app.application.ports.event_bus import EventBus
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import TaskStatus
from app.domain.models.value_objects import TaskId, UtcDateTime


class CompleteTaskUseCase:
    """Use case for completing a task (UC-045)."""

    def __init__(self, uow: UnitOfWork, event_bus: EventBus):
        self.uow = uow
        self.event_bus = event_bus

    def execute(self, task_id: TaskId) -> TaskOutput:
        """Complete a task."""
        with self.uow:
            task = self.uow.tasks.find_by_id(task_id)
            if task is None:
                raise BusinessRuleViolation("Task not found", code="task_not_found")

            task.transition_to(TaskStatus.DONE)
            if task.actual_end_date is None:
                task.actual_end_date = UtcDateTime.now()
            self.uow.tasks.save(task)
            self.uow.commit()

            self.event_bus.emit(TaskCompleted(task_id=task.id))
            return TaskOutput.from_domain(task)
