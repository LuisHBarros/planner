"""UC-031: Set Task Difficulty (manual) use case."""
from app.application.dtos.task_dtos import SetTaskDifficultyInput, TaskOutput
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation


class SetTaskDifficultyManualUseCase:
    """Use case for setting task difficulty manually (UC-031)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, input_dto: SetTaskDifficultyInput) -> TaskOutput:
        """Set task difficulty manually."""
        with self.uow:
            task = self.uow.tasks.find_by_id(input_dto.task_id)
            if task is None:
                raise BusinessRuleViolation("Task not found", code="task_not_found")
            task.difficulty = input_dto.difficulty
            self.uow.tasks.save(task)
            self.uow.commit()
            return TaskOutput.from_domain(task)
