"""UC-080: Send Manager Daily Report use case."""
from app.application.dtos.notification_dtos import NotificationRequestInput
from app.application.events.domain_events import NotificationRequested
from app.application.ports.event_bus import EventBus


class SendManagerDailyReportUseCase:
    """Use case for sending manager daily report (UC-080)."""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    def execute(self, input_dto: NotificationRequestInput) -> None:
        """Request manager daily report notification."""
        self.event_bus.emit(NotificationRequested(
            notification_type="manager_daily_report",
            project_id=input_dto.project_id,
            user_id=input_dto.user_id,
        ))
