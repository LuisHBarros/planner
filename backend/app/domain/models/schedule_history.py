"""ScheduleHistory domain model for tracking schedule changes."""
from datetime import datetime, UTC
from typing import Optional
from uuid import UUID, uuid4

from app.domain.models.enums import ScheduleChangeReason


class ScheduleHistory:
    """Immutable record of a task schedule change (Spec 2.0 - ScheduleHistory)."""

    def __init__(
        self,
        id: UUID,
        task_id: UUID,
        old_expected_start: Optional[datetime],
        old_expected_end: Optional[datetime],
        new_expected_start: Optional[datetime],
        new_expected_end: Optional[datetime],
        reason: ScheduleChangeReason,
        caused_by_task_id: Optional[UUID],
        changed_by_user_id: Optional[UUID],
        created_at: datetime,
    ) -> None:
        self.id = id
        self.task_id = task_id
        self.old_expected_start = old_expected_start
        self.old_expected_end = old_expected_end
        self.new_expected_start = new_expected_start
        self.new_expected_end = new_expected_end
        self.reason = reason
        self.caused_by_task_id = caused_by_task_id
        self.changed_by_user_id = changed_by_user_id
        self.created_at = created_at

    @classmethod
    def create(
        cls,
        task_id: UUID,
        old_expected_start: Optional[datetime],
        old_expected_end: Optional[datetime],
        new_expected_start: Optional[datetime],
        new_expected_end: Optional[datetime],
        reason: ScheduleChangeReason,
        caused_by_task_id: Optional[UUID] = None,
        changed_by_user_id: Optional[UUID] = None,
    ) -> "ScheduleHistory":
        """Factory method enforcing immutability semantics."""
        return cls(
            id=uuid4(),
            task_id=task_id,
            old_expected_start=old_expected_start,
            old_expected_end=old_expected_end,
            new_expected_start=new_expected_start,
            new_expected_end=new_expected_end,
            reason=reason,
            caused_by_task_id=caused_by_task_id,
            changed_by_user_id=changed_by_user_id,
            created_at=datetime.now(UTC),
        )

