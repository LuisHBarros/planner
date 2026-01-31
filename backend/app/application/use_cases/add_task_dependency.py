"""UC-033: Add Task Dependency use case."""
from app.application.dtos.task_dtos import TaskDependencyInput
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.task_dependency import TaskDependency


class AddTaskDependencyUseCase:
    """Use case for adding a task dependency (UC-033)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, input_dto: TaskDependencyInput) -> None:
        """Add a dependency between tasks."""
        if input_dto.task_id == input_dto.depends_on_id:
            raise BusinessRuleViolation("Task cannot depend on itself", code="self_dependency")

        with self.uow:
            dependency = TaskDependency.create(
                task_id=input_dto.task_id,
                depends_on_id=input_dto.depends_on_id,
            )
            self.uow.task_dependencies.save(dependency)
            self.uow.commit()
