"""Email preferences domain model."""
from datetime import datetime, UTC
from typing import Optional
from uuid import UUID, uuid4


class EmailPreferences:
    """Email preferences entity."""

    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        task_created: bool = True,
        task_assigned: bool = True,
        due_date_reminder: bool = True,
        task_completed: bool = False,
        task_blocked: bool = True,
        task_unblocked: bool = True,
        digest_mode: str = "daily",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.user_id = user_id
        self.task_created = task_created
        self.task_assigned = task_assigned
        self.due_date_reminder = due_date_reminder
        self.task_completed = task_completed
        self.task_blocked = task_blocked
        self.task_unblocked = task_unblocked
        self.digest_mode = digest_mode
        self.created_at = created_at or datetime.now(UTC)
        self.updated_at = updated_at or datetime.now(UTC)

    @classmethod
    def create_default(cls, user_id: UUID) -> "EmailPreferences":
        """Create default email preferences for a user."""
        return cls(
            id=uuid4(),
            user_id=user_id,
        )
