"""UC-081: Send Workload Alert use case."""
from app.application.dtos.notification_dtos import NotificationRequestInput
from app.application.events.domain_events import NotificationRequested
from app.application.ports.event_bus import EventBus


class SendWorkloadAlertUseCase:
    """Use case for sending workload alert (UC-081)."""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    def execute(self, input_dto: NotificationRequestInput) -> None:
        """Request workload alert notification."""
        self.event_bus.emit(NotificationRequested(
            notification_type="workload_alert",
            project_id=input_dto.project_id,
            user_id=input_dto.user_id,
        ))
