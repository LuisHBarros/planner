"""NotificationPreference repository port."""
from typing import Protocol, Optional

from app.domain.models.notification_preference import NotificationPreference
from app.domain.models.value_objects import ProjectId, UserId


class NotificationPreferenceRepository(Protocol):
    """Repository interface for NotificationPreference entities."""

    def save(self, preference: NotificationPreference) -> None:
        """Persist notification preferences."""
        ...

    def find_by_user_and_project(
        self,
        user_id: UserId,
        project_id: ProjectId,
    ) -> Optional[NotificationPreference]:
        """Find preferences for a user in a project."""
        ...
