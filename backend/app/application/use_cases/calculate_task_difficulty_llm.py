"""UC-032: Calculate Task Difficulty (LLM) use case."""
from app.application.dtos.task_dtos import TaskOutput
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.value_objects import TaskId


class CalculateTaskDifficultyLlmUseCase:
    """Use case for calculating task difficulty with LLM (UC-032)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, task_id: TaskId) -> TaskOutput:
        """Calculate task difficulty via LLM and persist."""
        with self.uow:
            task = self.uow.tasks.find_by_id(task_id)
            if task is None:
                raise BusinessRuleViolation("Task not found", code="task_not_found")

            difficulty = self.uow.llm_service.calculate_task_difficulty(task)
            task.difficulty = difficulty
            self.uow.tasks.save(task)
            self.uow.commit()
            return TaskOutput.from_domain(task)
