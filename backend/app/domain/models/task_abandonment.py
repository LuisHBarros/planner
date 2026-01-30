"""TaskAbandonment domain model (v3.0)."""
from datetime import datetime, UTC
from typing import Optional
from uuid import UUID, uuid4

from app.domain.models.enums import AbandonmentType


class TaskAbandonment:
    """
    Task abandonment entity for recording abandonment details (v3.0).

    This is separate from TaskAssignmentHistory to capture additional
    context about why a task was abandoned.

    Attributes:
        id: Unique identifier
        task_id: The task that was abandoned
        user_id: The user who was working on the task
        abandonment_type: The type of abandonment
        reason: Optional explanation for the abandonment
        initiated_by_user_id: The user who initiated the abandonment
            (could be different from user_id for FIRED_FROM_TASK, etc.)
        created_at: When the abandonment occurred
    """

    def __init__(
        self,
        id: UUID,
        task_id: UUID,
        user_id: UUID,
        abandonment_type: AbandonmentType,
        initiated_by_user_id: UUID,
        reason: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.task_id = task_id
        self.user_id = user_id
        self.abandonment_type = abandonment_type
        self.reason = reason
        self.initiated_by_user_id = initiated_by_user_id
        self.created_at = created_at or datetime.now(UTC)

    @classmethod
    def create(
        cls,
        task_id: UUID,
        user_id: UUID,
        abandonment_type: AbandonmentType,
        initiated_by_user_id: UUID,
        reason: Optional[str] = None,
    ) -> "TaskAbandonment":
        """Create a new task abandonment record."""
        return cls(
            id=uuid4(),
            task_id=task_id,
            user_id=user_id,
            abandonment_type=abandonment_type,
            initiated_by_user_id=initiated_by_user_id,
            reason=reason,
        )

    @classmethod
    def voluntary(
        cls,
        task_id: UUID,
        user_id: UUID,
        reason: Optional[str] = None,
    ) -> "TaskAbandonment":
        """Create a voluntary abandonment (employee abandons own task)."""
        return cls.create(
            task_id=task_id,
            user_id=user_id,
            abandonment_type=AbandonmentType.VOLUNTARY,
            initiated_by_user_id=user_id,
            reason=reason,
        )

    @classmethod
    def fired_from_task(
        cls,
        task_id: UUID,
        user_id: UUID,
        manager_id: UUID,
        reason: Optional[str] = None,
    ) -> "TaskAbandonment":
        """Create a fired-from-task abandonment (manager removes employee from task)."""
        return cls.create(
            task_id=task_id,
            user_id=user_id,
            abandonment_type=AbandonmentType.FIRED_FROM_TASK,
            initiated_by_user_id=manager_id,
            reason=reason,
        )

    @classmethod
    def fired_from_project(
        cls,
        task_id: UUID,
        user_id: UUID,
        manager_id: UUID,
        reason: Optional[str] = None,
    ) -> "TaskAbandonment":
        """Create a fired-from-project abandonment (manager fires employee)."""
        return cls.create(
            task_id=task_id,
            user_id=user_id,
            abandonment_type=AbandonmentType.FIRED_FROM_PROJECT,
            initiated_by_user_id=manager_id,
            reason=reason,
        )

    @classmethod
    def resigned(
        cls,
        task_id: UUID,
        user_id: UUID,
        reason: Optional[str] = None,
    ) -> "TaskAbandonment":
        """Create a resignation abandonment (employee resigns)."""
        return cls.create(
            task_id=task_id,
            user_id=user_id,
            abandonment_type=AbandonmentType.RESIGNED,
            initiated_by_user_id=user_id,
            reason=reason,
        )

    @classmethod
    def task_cancelled(
        cls,
        task_id: UUID,
        user_id: UUID,
        cancelled_by_user_id: UUID,
        reason: Optional[str] = None,
    ) -> "TaskAbandonment":
        """Create a task-cancelled abandonment."""
        return cls.create(
            task_id=task_id,
            user_id=user_id,
            abandonment_type=AbandonmentType.TASK_CANCELLED,
            initiated_by_user_id=cancelled_by_user_id,
            reason=reason,
        )

    def is_voluntary(self) -> bool:
        """Check if this was a voluntary abandonment."""
        return self.abandonment_type == AbandonmentType.VOLUNTARY

    def is_manager_initiated(self) -> bool:
        """Check if this abandonment was initiated by a manager."""
        return self.abandonment_type in [
            AbandonmentType.FIRED_FROM_TASK,
            AbandonmentType.FIRED_FROM_PROJECT,
            AbandonmentType.TASK_CANCELLED,
        ]
