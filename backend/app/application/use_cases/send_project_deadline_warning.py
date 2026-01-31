"""UC-084: Send Project Deadline Warning use case."""
from app.application.dtos.notification_dtos import NotificationRequestInput
from app.application.events.domain_events import NotificationRequested
from app.application.ports.event_bus import EventBus


class SendProjectDeadlineWarningUseCase:
    """Use case for sending project deadline warning (UC-084)."""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    def execute(self, input_dto: NotificationRequestInput) -> None:
        """Request project deadline warning notification."""
        self.event_bus.emit(NotificationRequested(
            notification_type="project_deadline_warning",
            project_id=input_dto.project_id,
        ))
