"""Daily report job scheduler."""
from __future__ import annotations

from threading import Timer

from app.application.events.domain_events import NotificationRequested
from app.infrastructure.events.in_memory_event_bus import InMemoryEventBus

_job_timer: Timer | None = None


def start_daily_report_job(event_bus: InMemoryEventBus, interval_seconds: int = 86400) -> None:
    """Start a repeating daily report job."""
    global _job_timer

    def _run():
        event_bus.emit(NotificationRequested(notification_type="manager_daily_report"))
        start_daily_report_job(event_bus, interval_seconds)

    _job_timer = Timer(interval_seconds, _run)
    _job_timer.daemon = True
    _job_timer.start()
