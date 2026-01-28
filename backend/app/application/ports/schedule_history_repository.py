"""Schedule history repository port."""
from typing import Protocol, List
from uuid import UUID

from app.domain.models.schedule_history import ScheduleHistory


class ScheduleHistoryRepository(Protocol):
    """Repository interface for ScheduleHistory entities."""

    def save(self, history: ScheduleHistory) -> None:
        """Persist a schedule history record (immutable)."""
        ...

    def find_by_task_id(self, task_id: UUID) -> List[ScheduleHistory]:
        """Return all schedule history records for a task, ordered by created_at."""
        ...

