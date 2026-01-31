"""TaskDependency repository port."""
from typing import Protocol, List

from app.domain.models.task_dependency import TaskDependency
from app.domain.models.value_objects import TaskId


class TaskDependencyRepository(Protocol):
    """Repository interface for TaskDependency entities."""

    def save(self, dependency: TaskDependency) -> None:
        """Persist a task dependency."""
        ...

    def list_by_task(self, task_id: TaskId) -> List[TaskDependency]:
        """List dependencies for a task."""
        ...

    def delete(self, task_id: TaskId, depends_on_id: TaskId) -> None:
        """Delete a dependency."""
        ...
