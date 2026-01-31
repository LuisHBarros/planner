"""Task notification handler."""
from __future__ import annotations

from app.application.events.domain_events import NotificationRequested
from app.infrastructure.notifications.notification_service import NotificationService


class TaskNotificationHandler:
    """Handler for task-related notifications."""

    def __init__(self, notification_service: NotificationService) -> None:
        self.notification_service = notification_service

    def handle(self, event: NotificationRequested) -> None:
        """Handle task-related notifications."""
        if event.notification_type == "new_task_toast":
            self.notification_service.send_new_task_toast(
                project_id=event.project_id,
                task_id=event.task_id,
                user_id=event.user_id,
            )
        elif event.notification_type == "employee_daily_email":
            self.notification_service.send_employee_daily_email(
                project_id=event.project_id,
                user_id=event.user_id,
            )
        elif event.notification_type == "manager_daily_report":
            self.notification_service.send_manager_daily_report(
                project_id=event.project_id,
                user_id=event.user_id,
            )
        elif event.notification_type == "project_deadline_warning":
            self.notification_service.send_project_deadline_warning(
                project_id=event.project_id,
            )
