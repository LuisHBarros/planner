"""TaskAssignmentHistory domain model (v3.0)."""
from datetime import datetime, UTC
from typing import Optional
from uuid import UUID, uuid4

from app.domain.models.enums import AssignmentAction, AbandonmentType


class TaskAssignmentHistory:
    """
    Task assignment history entity for tracking assignment lifecycle (v3.0).

    Records all assignment actions: STARTED, ABANDONED, RESUMED, COMPLETED.
    This is an append-only log of assignment events.

    Attributes:
        id: Unique identifier
        task_id: The task this history relates to
        user_id: The user who performed or was subject to the action
        action: The type of action (STARTED, ABANDONED, RESUMED, COMPLETED)
        abandonment_type: Type of abandonment (only set when action=ABANDONED)
        created_at: When the action occurred
    """

    def __init__(
        self,
        id: UUID,
        task_id: UUID,
        user_id: UUID,
        action: AssignmentAction,
        abandonment_type: Optional[AbandonmentType] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.task_id = task_id
        self.user_id = user_id
        self.action = action
        self.abandonment_type = abandonment_type
        self.created_at = created_at or datetime.now(UTC)

    @classmethod
    def create(
        cls,
        task_id: UUID,
        user_id: UUID,
        action: AssignmentAction,
        abandonment_type: Optional[AbandonmentType] = None,
    ) -> "TaskAssignmentHistory":
        """Create a new assignment history record."""
        return cls(
            id=uuid4(),
            task_id=task_id,
            user_id=user_id,
            action=action,
            abandonment_type=abandonment_type,
        )

    @classmethod
    def record_started(cls, task_id: UUID, user_id: UUID) -> "TaskAssignmentHistory":
        """Record that a user started working on a task."""
        return cls.create(
            task_id=task_id,
            user_id=user_id,
            action=AssignmentAction.STARTED,
        )

    @classmethod
    def record_abandoned(
        cls,
        task_id: UUID,
        user_id: UUID,
        abandonment_type: AbandonmentType,
    ) -> "TaskAssignmentHistory":
        """Record that a task was abandoned."""
        return cls.create(
            task_id=task_id,
            user_id=user_id,
            action=AssignmentAction.ABANDONED,
            abandonment_type=abandonment_type,
        )

    @classmethod
    def record_resumed(cls, task_id: UUID, user_id: UUID) -> "TaskAssignmentHistory":
        """Record that a user resumed working on a task."""
        return cls.create(
            task_id=task_id,
            user_id=user_id,
            action=AssignmentAction.RESUMED,
        )

    @classmethod
    def record_completed(cls, task_id: UUID, user_id: UUID) -> "TaskAssignmentHistory":
        """Record that a task was completed."""
        return cls.create(
            task_id=task_id,
            user_id=user_id,
            action=AssignmentAction.COMPLETED,
        )
