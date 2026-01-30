"""Port for TaskAbandonment repository (v3.0)."""
from typing import List, Optional, Protocol
from uuid import UUID

from app.domain.models.task_abandonment import TaskAbandonment


class TaskAbandonmentRepository(Protocol):
    """Repository interface for TaskAbandonment entities."""

    def save(self, abandonment: TaskAbandonment) -> None:
        """Persist a task abandonment record."""
        ...

    def find_by_id(self, abandonment_id: UUID) -> Optional[TaskAbandonment]:
        """Find an abandonment record by ID."""
        ...

    def find_by_task_id(self, task_id: UUID) -> List[TaskAbandonment]:
        """Find all abandonment records for a task, ordered by created_at."""
        ...

    def find_by_user_id(self, user_id: UUID) -> List[TaskAbandonment]:
        """Find all abandonment records for a user, ordered by created_at."""
        ...

    def find_by_initiated_by_user_id(
        self, initiated_by_user_id: UUID
    ) -> List[TaskAbandonment]:
        """Find all abandonments initiated by a specific user."""
        ...
