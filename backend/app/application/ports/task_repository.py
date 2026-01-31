"""Task repository port."""
from typing import Protocol, Optional, List

from app.domain.models.task import Task
from app.domain.models.value_objects import ProjectId, TaskId


class TaskRepository(Protocol):
    """Repository interface for Task entities."""

    def save(self, task: Task) -> None:
        """Persist a task."""
        ...

    def find_by_id(self, task_id: TaskId) -> Optional[Task]:
        """Find task by ID."""
        ...

    def list_by_project(self, project_id: ProjectId) -> List[Task]:
        """List tasks in a project."""
        ...
