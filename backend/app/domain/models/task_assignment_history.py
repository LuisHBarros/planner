"""TaskAssignmentHistory domain model."""
from dataclasses import dataclass, field
from typing import Optional

from app.domain.models.value_objects import (
    TaskAssignmentHistoryId,
    TaskId,
    UserId,
    UtcDateTime,
)


@dataclass
class TaskAssignmentHistory:
    """Audit record for task assignments."""
    id: TaskAssignmentHistoryId
    task_id: TaskId
    user_id: UserId
    assigned_at: UtcDateTime
    unassigned_at: Optional[UtcDateTime]
    assignment_reason: Optional[str]

    @classmethod
    def create(
        cls,
        task_id: TaskId,
        user_id: UserId,
        assignment_reason: Optional[str] = None,
    ) -> "TaskAssignmentHistory":
        """Create a task assignment history record."""
        return cls(
            id=TaskAssignmentHistoryId(),
            task_id=task_id,
            user_id=user_id,
            assigned_at=UtcDateTime.now(),
            unassigned_at=None,
            assignment_reason=assignment_reason,
        )
