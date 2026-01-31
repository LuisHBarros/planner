"""UC-034: Remove Task Dependency use case."""
from app.application.dtos.task_dtos import TaskDependencyInput
from app.application.ports.unit_of_work import UnitOfWork


class RemoveTaskDependencyUseCase:
    """Use case for removing a task dependency (UC-034)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, input_dto: TaskDependencyInput) -> None:
        """Remove a dependency between tasks."""
        with self.uow:
            self.uow.task_dependencies.delete(
                task_id=input_dto.task_id,
                depends_on_id=input_dto.depends_on_id,
            )
            self.uow.commit()
