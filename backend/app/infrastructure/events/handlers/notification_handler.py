"""Notification handler registration."""
from __future__ import annotations

from app.application.events.domain_events import NotificationRequested
from app.infrastructure.events.in_memory_event_bus import InMemoryEventBus
from app.infrastructure.notifications.handlers.task_handler import TaskNotificationHandler
from app.infrastructure.notifications.handlers.workload_handler import WorkloadNotificationHandler
from app.infrastructure.notifications.notification_service import NotificationService


def register_notification_handlers(
    event_bus: InMemoryEventBus,
    notification_service: NotificationService,
) -> None:
    """Register notification handlers with the event bus."""
    workload_handler = WorkloadNotificationHandler(notification_service)
    task_handler = TaskNotificationHandler(notification_service)

    event_bus.register(NotificationRequested, workload_handler.handle)
    event_bus.register(NotificationRequested, task_handler.handle)
