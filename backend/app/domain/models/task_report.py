"""TaskReport domain model."""
from dataclasses import dataclass, field
from typing import Optional

from app.domain.models.enums import ProgressSource
from app.domain.models.value_objects import TaskId, TaskReportId, UserId, UtcDateTime


@dataclass
class TaskReport:
    """Progress report for a task."""
    id: TaskReportId
    task_id: TaskId
    author_id: UserId
    progress: int
    source: ProgressSource
    note: Optional[str]
    created_at: UtcDateTime = field(default_factory=UtcDateTime.now)

    @classmethod
    def create(
        cls,
        task_id: TaskId,
        author_id: UserId,
        progress: int,
        source: ProgressSource,
        note: Optional[str] = None,
    ) -> "TaskReport":
        """Create a task report."""
        return cls(
            id=TaskReportId(),
            task_id=task_id,
            author_id=author_id,
            progress=progress,
            source=source,
            note=note,
        )
