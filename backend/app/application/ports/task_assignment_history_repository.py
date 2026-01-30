"""Port for TaskAssignmentHistory repository (v3.0)."""
from typing import List, Optional, Protocol
from uuid import UUID

from app.domain.models.task_assignment_history import TaskAssignmentHistory


class TaskAssignmentHistoryRepository(Protocol):
    """Repository interface for TaskAssignmentHistory entities."""

    def save(self, history: TaskAssignmentHistory) -> None:
        """Persist an assignment history record (append-only)."""
        ...

    def find_by_id(self, history_id: UUID) -> Optional[TaskAssignmentHistory]:
        """Find an assignment history record by ID."""
        ...

    def find_by_task_id(self, task_id: UUID) -> List[TaskAssignmentHistory]:
        """Find all assignment history for a task, ordered by created_at."""
        ...

    def find_by_user_id(self, user_id: UUID) -> List[TaskAssignmentHistory]:
        """Find all assignment history for a user, ordered by created_at."""
        ...

    def find_by_task_and_user(
        self, task_id: UUID, user_id: UUID
    ) -> List[TaskAssignmentHistory]:
        """Find assignment history for a specific task and user combination."""
        ...
