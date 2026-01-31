"""Tests for NotificationPreference entity."""
from app.domain.models.notification_preference import NotificationPreference
from app.domain.models.value_objects import ProjectId, UserId


def test_notification_preference_defaults():
    """NotificationPreference.create sets defaults."""
    preference = NotificationPreference.create(
        project_id=ProjectId(),
        user_id=UserId(),
    )
    assert preference.email_enabled is True
    assert preference.toast_enabled is True
