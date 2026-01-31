"""UC-041: Abandon Task use case."""
from app.application.dtos.task_dtos import AbandonTaskInput, TaskOutput
from app.application.events.domain_events import TaskAbandoned
from app.application.ports.event_bus import EventBus
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import TaskStatus
from app.domain.models.task_abandonment import TaskAbandonment


class AbandonTaskUseCase:
    """Use case for abandoning a task (UC-041)."""

    def __init__(self, uow: UnitOfWork, event_bus: EventBus):
        self.uow = uow
        self.event_bus = event_bus

    def execute(self, input_dto: AbandonTaskInput) -> TaskOutput:
        """Abandon a task."""
        with self.uow:
            task = self.uow.tasks.find_by_id(input_dto.task_id)
            if task is None:
                raise BusinessRuleViolation("Task not found", code="task_not_found")

            if task.assigned_to != input_dto.user_id:
                raise BusinessRuleViolation(
                    "Task not assigned to user",
                    code="task_not_assigned",
                )

            task.assigned_to = None
            if task.status == TaskStatus.DOING:
                task.transition_to(TaskStatus.TODO)
            self.uow.tasks.save(task)

            abandonment = TaskAbandonment.create(
                task_id=task.id,
                user_id=input_dto.user_id,
                abandonment_type=input_dto.abandonment_type,
                note=input_dto.note,
            )
            self.uow.task_abandonments.save(abandonment)

            self.uow.commit()

            self.event_bus.emit(TaskAbandoned(
                task_id=task.id,
                user_id=input_dto.user_id,
                abandonment_type=input_dto.abandonment_type,
            ))

            return TaskOutput.from_domain(task)
