"""UC-082: Send New Task Toast use case."""
from app.application.dtos.notification_dtos import NotificationRequestInput
from app.application.events.domain_events import NotificationRequested
from app.application.ports.event_bus import EventBus


class SendNewTaskToastUseCase:
    """Use case for sending new task toast (UC-082)."""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    def execute(self, input_dto: NotificationRequestInput) -> None:
        """Request new task toast notification."""
        self.event_bus.emit(NotificationRequested(
            notification_type="new_task_toast",
            project_id=input_dto.project_id,
            task_id=input_dto.task_id,
            user_id=input_dto.user_id,
        ))
