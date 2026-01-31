"""UC-083: Send Employee Daily Email use case."""
from app.application.dtos.notification_dtos import NotificationRequestInput
from app.application.events.domain_events import NotificationRequested
from app.application.ports.event_bus import EventBus


class SendEmployeeDailyEmailUseCase:
    """Use case for sending employee daily email (UC-083)."""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    def execute(self, input_dto: NotificationRequestInput) -> None:
        """Request employee daily email notification."""
        self.event_bus.emit(NotificationRequested(
            notification_type="employee_daily_email",
            project_id=input_dto.project_id,
            user_id=input_dto.user_id,
        ))
