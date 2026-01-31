"""UC-050: Remove from Task use case."""
from app.application.dtos.task_dtos import TaskOutput
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import TaskStatus
from app.domain.models.task_assignment_history import TaskAssignmentHistory
from app.domain.models.value_objects import TaskId, UserId


class RemoveFromTaskUseCase:
    """Use case for removing a user from a task (UC-050)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, task_id: TaskId, user_id: UserId) -> TaskOutput:
        """Remove a user from a task."""
        with self.uow:
            task = self.uow.tasks.find_by_id(task_id)
            if task is None:
                raise BusinessRuleViolation("Task not found", code="task_not_found")
            if task.assigned_to != user_id:
                raise BusinessRuleViolation("Task not assigned to user", code="task_not_assigned")

            task.assigned_to = None
            if task.status == TaskStatus.DOING:
                task.transition_to(TaskStatus.TODO)
            self.uow.tasks.save(task)

            history = TaskAssignmentHistory.create(
                task_id=task.id,
                user_id=user_id,
                assignment_reason="remove_from_task",
            )
            self.uow.task_assignment_history.save(history)

            self.uow.commit()
            return TaskOutput.from_domain(task)
