"""Schedule history repository port."""
from typing import Protocol, List
from uuid import UUID

from app.domain.models.schedule_history import ScheduleHistory


class ScheduleHistoryRepository(Protocol):
    """Repository interface for ScheduleHistory entities.

    This repository is append-only (immutable records).
    ScheduleHistory records NEVER change - new changes create new records.
    """

    def save(self, history: ScheduleHistory) -> None:
        """Persist a schedule history record (immutable append-only)."""
        ...

    def find_by_task_id(self, task_id: UUID) -> List[ScheduleHistory]:
        """Return all schedule history records for a task, ordered by created_at."""
        ...

    def find_by_caused_by_task_id(self, caused_by_task_id: UUID) -> List[ScheduleHistory]:
        """Return all schedule history records caused by a specific task."""
        ...

