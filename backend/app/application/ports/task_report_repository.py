"""TaskReport repository port."""
from typing import Protocol, List

from app.domain.models.task_report import TaskReport
from app.domain.models.value_objects import TaskId


class TaskReportRepository(Protocol):
    """Repository interface for TaskReport entities."""

    def save(self, report: TaskReport) -> None:
        """Persist a task report."""
        ...

    def list_by_task(self, task_id: TaskId) -> List[TaskReport]:
        """List reports for a task."""
        ...
