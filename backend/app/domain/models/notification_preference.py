"""NotificationPreference domain model."""
from dataclasses import dataclass, field

from app.domain.models.value_objects import (
    NotificationPreferenceId,
    ProjectId,
    UserId,
    UtcDateTime,
)


@dataclass
class NotificationPreference:
    """Notification preferences for a user within a project."""
    id: NotificationPreferenceId
    project_id: ProjectId
    user_id: UserId
    email_enabled: bool
    toast_enabled: bool
    created_at: UtcDateTime = field(default_factory=UtcDateTime.now)

    @classmethod
    def create(
        cls,
        project_id: ProjectId,
        user_id: UserId,
        email_enabled: bool = True,
        toast_enabled: bool = True,
    ) -> "NotificationPreference":
        """Create notification preferences."""
        return cls(
            id=NotificationPreferenceId(),
            project_id=project_id,
            user_id=user_id,
            email_enabled=email_enabled,
            toast_enabled=toast_enabled,
        )
