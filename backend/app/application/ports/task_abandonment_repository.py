"""TaskAbandonment repository port."""
from typing import Protocol, List

from app.domain.models.task_abandonment import TaskAbandonment
from app.domain.models.value_objects import TaskId


class TaskAbandonmentRepository(Protocol):
    """Repository interface for TaskAbandonment entities."""

    def save(self, abandonment: TaskAbandonment) -> None:
        """Persist a task abandonment."""
        ...

    def list_by_task(self, task_id: TaskId) -> List[TaskAbandonment]:
        """List abandonments for a task."""
        ...
