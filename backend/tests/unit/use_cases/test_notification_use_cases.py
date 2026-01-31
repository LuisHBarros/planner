"""Tests for notification use cases."""
from unittest.mock import Mock

from app.application.dtos.notification_dtos import NotificationRequestInput
from app.application.use_cases.send_employee_daily_email import SendEmployeeDailyEmailUseCase
from app.application.use_cases.send_manager_daily_report import SendManagerDailyReportUseCase
from app.application.use_cases.send_new_task_toast import SendNewTaskToastUseCase
from app.application.use_cases.send_project_deadline_warning import SendProjectDeadlineWarningUseCase
from app.application.use_cases.send_workload_alert import SendWorkloadAlertUseCase
from app.domain.models.value_objects import ProjectId, TaskId, UserId


def test_notification_use_cases_emit_events():
    """All notification use cases emit events."""
    event_bus = Mock()
    input_dto = NotificationRequestInput(
        notification_type="any",
        project_id=ProjectId(),
        task_id=TaskId(),
        user_id=UserId(),
    )

    SendManagerDailyReportUseCase(event_bus).execute(input_dto)
    SendWorkloadAlertUseCase(event_bus).execute(input_dto)
    SendNewTaskToastUseCase(event_bus).execute(input_dto)
    SendEmployeeDailyEmailUseCase(event_bus).execute(input_dto)
    SendProjectDeadlineWarningUseCase(event_bus).execute(input_dto)

    assert event_bus.emit.call_count == 5
