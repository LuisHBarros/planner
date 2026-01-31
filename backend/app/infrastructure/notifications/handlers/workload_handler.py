"""Workload notification handler."""
from __future__ import annotations

from app.application.events.domain_events import NotificationRequested
from app.infrastructure.notifications.notification_service import NotificationService


class WorkloadNotificationHandler:
    """Handler for workload alerts."""

    def __init__(self, notification_service: NotificationService) -> None:
        self.notification_service = notification_service

    def handle(self, event: NotificationRequested) -> None:
        """Handle workload alert notifications."""
        if event.notification_type != "workload_alert":
            return
        self.notification_service.send_workload_alert(
            project_id=event.project_id,
            user_id=event.user_id,
        )
