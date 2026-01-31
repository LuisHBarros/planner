"""TaskAbandonment domain model."""
from dataclasses import dataclass, field
from typing import Optional

from app.domain.models.enums import AbandonmentType
from app.domain.models.value_objects import TaskAbandonmentId, TaskId, UserId, UtcDateTime


@dataclass
class TaskAbandonment:
    """Record of a task abandonment."""
    id: TaskAbandonmentId
    task_id: TaskId
    user_id: UserId
    abandonment_type: AbandonmentType
    note: Optional[str]
    created_at: UtcDateTime = field(default_factory=UtcDateTime.now)

    @classmethod
    def create(
        cls,
        task_id: TaskId,
        user_id: UserId,
        abandonment_type: AbandonmentType,
        note: Optional[str] = None,
    ) -> "TaskAbandonment":
        """Create a task abandonment record."""
        return cls(
            id=TaskAbandonmentId(),
            task_id=task_id,
            user_id=user_id,
            abandonment_type=abandonment_type,
            note=note,
        )
