"""TaskScheduleHistory domain model."""
from dataclasses import dataclass, field

from app.domain.models.enums import ScheduleChangeReason
from app.domain.models.value_objects import (
    TaskId,
    TaskScheduleHistoryId,
    UtcDateTime,
)


@dataclass
class TaskScheduleHistory:
    """Audit record for task schedule changes."""
    id: TaskScheduleHistoryId
    task_id: TaskId
    previous_start: UtcDateTime
    previous_end: UtcDateTime
    new_start: UtcDateTime
    new_end: UtcDateTime
    reason: ScheduleChangeReason
    created_at: UtcDateTime = field(default_factory=UtcDateTime.now)

    @classmethod
    def create(
        cls,
        task_id: TaskId,
        previous_start: UtcDateTime,
        previous_end: UtcDateTime,
        new_start: UtcDateTime,
        new_end: UtcDateTime,
        reason: ScheduleChangeReason,
    ) -> "TaskScheduleHistory":
        """Create a task schedule history record."""
        return cls(
            id=TaskScheduleHistoryId(),
            task_id=task_id,
            previous_start=previous_start,
            previous_end=previous_end,
            new_start=new_start,
            new_end=new_end,
            reason=reason,
        )
