"""Tests for notification handlers."""
from app.application.events.domain_events import NotificationRequested
from app.infrastructure.notifications.handlers.task_handler import TaskNotificationHandler
from app.infrastructure.notifications.handlers.workload_handler import WorkloadNotificationHandler
from app.infrastructure.notifications.notification_service import NotificationService


def test_workload_handler_sends_alert():
    """Workload handler sends workload alert."""
    service = NotificationService()
    handler = WorkloadNotificationHandler(service)
    event = NotificationRequested(notification_type="workload_alert", project_id=None, user_id=None)

    handler.handle(event)

    assert service.sent[0]["type"] == "workload_alert"


def test_task_handler_sends_new_task_toast():
    """Task handler sends new task toast."""
    service = NotificationService()
    handler = TaskNotificationHandler(service)
    event = NotificationRequested(notification_type="new_task_toast", project_id=None, task_id=None, user_id=None)

    handler.handle(event)

    assert service.sent[0]["type"] == "new_task_toast"
