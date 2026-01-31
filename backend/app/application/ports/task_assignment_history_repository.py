"""TaskAssignmentHistory repository port."""
from typing import Protocol, List

from app.domain.models.task_assignment_history import TaskAssignmentHistory
from app.domain.models.value_objects import TaskId


class TaskAssignmentHistoryRepository(Protocol):
    """Repository interface for TaskAssignmentHistory entities."""

    def save(self, history: TaskAssignmentHistory) -> None:
        """Persist a task assignment history record."""
        ...

    def list_by_task(self, task_id: TaskId) -> List[TaskAssignmentHistory]:
        """List assignment history for a task."""
        ...
