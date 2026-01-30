"""Task repository port."""
from typing import Protocol, Optional, List, Union
from uuid import UUID
from app.domain.models.task import Task
from app.domain.models.enums import TaskStatus
from app.domain.models.value_objects import TaskId, ProjectId, RoleId, UserId


class TaskRepository(Protocol):
    """Repository interface for Task entities.

    Accepts both value objects and raw UUIDs for backward compatibility.
    """

    def save(self, task: Task) -> None:
        """Save a task."""
        ...

    def find_by_id(self, task_id: Union[TaskId, UUID]) -> Optional[Task]:
        """Find task by ID."""
        ...

    def find_by_project_id(self, project_id: Union[ProjectId, UUID]) -> List[Task]:
        """Find all tasks for a project, ordered by rank_index."""
        ...

    def find_by_role_id(
        self, role_id: Union[RoleId, UUID], status: Optional[TaskStatus] = None
    ) -> List[Task]:
        """Find tasks by role, optionally filtered by status."""
        ...

    def find_by_user_id(self, user_id: Union[UserId, UUID]) -> List[Task]:
        """Find all tasks assigned to a user."""
        ...

    def find_dependent_tasks(self, task_id: Union[TaskId, UUID]) -> List[Task]:
        """Find all tasks that depend on the given task."""
        ...
