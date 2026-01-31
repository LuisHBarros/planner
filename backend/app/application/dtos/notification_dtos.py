"""Notification DTOs."""
from dataclasses import dataclass

from app.domain.models.value_objects import ProjectId, TaskId, UserId


@dataclass(frozen=True)
class NotificationRequestInput:
    """Input for notification requests."""
    notification_type: str
    project_id: ProjectId | None = None
    task_id: TaskId | None = None
    user_id: UserId | None = None
