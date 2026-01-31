"""UC-030: Create Task use case."""
from app.application.dtos.task_dtos import CreateTaskInput, TaskOutput
from app.application.events.domain_events import TaskCreated
from app.application.ports.event_bus import EventBus
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.task import Task


class CreateTaskUseCase:
    """Use case for creating a task (UC-030)."""

    def __init__(self, uow: UnitOfWork, event_bus: EventBus):
        self.uow = uow
        self.event_bus = event_bus

    def execute(self, input_dto: CreateTaskInput) -> TaskOutput:
        """Create a new task."""
        with self.uow:
            project = self.uow.projects.find_by_id(input_dto.project_id)
            if project is None:
                raise BusinessRuleViolation("Project not found", code="project_not_found")

            task = Task.create(
                project_id=input_dto.project_id,
                title=input_dto.title,
                description=input_dto.description,
            )
            task.role_id = input_dto.role_id
            self.uow.tasks.save(task)
            self.uow.commit()

            self.event_bus.emit(TaskCreated(task_id=task.id, project_id=task.project_id))
            return TaskOutput.from_domain(task)
