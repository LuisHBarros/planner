"""Schedule history repository port."""
from typing import Protocol, List

from app.domain.models.project_schedule_history import ProjectScheduleHistory
from app.domain.models.task_schedule_history import TaskScheduleHistory
from app.domain.models.value_objects import ProjectId, TaskId


class ScheduleHistoryRepository(Protocol):
    """Repository interface for schedule history entities."""

    def save_task_history(self, history: TaskScheduleHistory) -> None:
        """Persist a task schedule history record."""
        ...

    def save_project_history(self, history: ProjectScheduleHistory) -> None:
        """Persist a project schedule history record."""
        ...

    def list_task_history(self, task_id: TaskId) -> List[TaskScheduleHistory]:
        """List schedule history for a task."""
        ...

    def list_project_history(self, project_id: ProjectId) -> List[ProjectScheduleHistory]:
        """List schedule history for a project."""
        ...
