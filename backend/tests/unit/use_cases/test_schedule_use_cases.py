"""Tests for schedule-related use cases."""
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.application.dtos.schedule_dtos import ManualDateOverrideInput, UpdateProjectDateInput
from app.application.use_cases.detect_delay import DetectDelayUseCase
from app.application.use_cases.manual_date_override import ManualDateOverrideUseCase
from app.application.use_cases.update_project_date import UpdateProjectDateUseCase
from app.application.use_cases.view_schedule_history import ViewScheduleHistoryUseCase
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import ScheduleChangeReason
from app.domain.models.project import Project
from app.domain.models.task import Task
from app.domain.models.task_schedule_history import TaskScheduleHistory
from app.domain.models.project_schedule_history import ProjectScheduleHistory
from app.domain.models.value_objects import ProjectId, TaskId, UtcDateTime, UserId


def test_detect_delay_returns_boolean():
    """Detects delay for a task."""
    uow = MagicMock()
    task = Task.create(project_id=ProjectId(), title="Task")
    task.expected_end_date = UtcDateTime(datetime(2024, 1, 1, tzinfo=timezone.utc))
    task.actual_end_date = UtcDateTime(datetime(2024, 1, 2, tzinfo=timezone.utc))
    uow.tasks.find_by_id.return_value = task
    use_case = DetectDelayUseCase(uow)

    assert use_case.execute(task.id) is True


def test_update_project_date_records_history():
    """Updates project date and records history."""
    uow = MagicMock()
    project = Project.create(name="Proj", created_by=UserId())
    project.expected_end_date = UtcDateTime(datetime(2024, 1, 1, tzinfo=timezone.utc))
    uow.projects.find_by_id.return_value = project
    use_case = UpdateProjectDateUseCase(uow)
    input_dto = UpdateProjectDateInput(
        project_id=project.id,
        new_end_date=UtcDateTime(datetime(2024, 1, 3, tzinfo=timezone.utc)),
        reason=ScheduleChangeReason.MANUAL_OVERRIDE,
    )

    use_case.execute(input_dto)

    uow.projects.save.assert_called_once()
    uow.schedule_history.save_project_history.assert_called_once()
    uow.commit.assert_called_once()


def test_manual_date_override_records_history():
    """Overrides task dates and records history."""
    uow = MagicMock()
    task = Task.create(project_id=ProjectId(), title="Task")
    task.expected_start_date = UtcDateTime(datetime(2024, 1, 1, tzinfo=timezone.utc))
    task.expected_end_date = UtcDateTime(datetime(2024, 1, 2, tzinfo=timezone.utc))
    uow.tasks.find_by_id.return_value = task
    use_case = ManualDateOverrideUseCase(uow)
    input_dto = ManualDateOverrideInput(
        task_id=task.id,
        new_start_date=UtcDateTime(datetime(2024, 1, 3, tzinfo=timezone.utc)),
        new_end_date=UtcDateTime(datetime(2024, 1, 4, tzinfo=timezone.utc)),
    )

    use_case.execute(input_dto)

    uow.tasks.save.assert_called_once()
    uow.schedule_history.save_task_history.assert_called_once()
    uow.commit.assert_called_once()


def test_view_schedule_history_returns_lists():
    """Returns project and task history."""
    uow = MagicMock()
    project_history = ProjectScheduleHistory.create(
        project_id=ProjectId(),
        previous_end=UtcDateTime(),
        new_end=UtcDateTime(),
        reason=ScheduleChangeReason.MANUAL_OVERRIDE,
    )
    task_history = TaskScheduleHistory.create(
        task_id=TaskId(),
        previous_start=UtcDateTime(),
        previous_end=UtcDateTime(),
        new_start=UtcDateTime(),
        new_end=UtcDateTime(),
        reason=ScheduleChangeReason.MANUAL_OVERRIDE,
    )
    uow.schedule_history.list_project_history.return_value = [project_history]
    uow.schedule_history.list_task_history.return_value = [task_history]
    use_case = ViewScheduleHistoryUseCase(uow)

    projects, tasks = use_case.execute(project_id=project_history.project_id, task_id=task_history.task_id)

    assert len(projects) == 1
    assert len(tasks) == 1


def test_detect_delay_fails_if_task_missing():
    """Fails if task missing."""
    uow = MagicMock()
    uow.tasks.find_by_id.return_value = None
    use_case = DetectDelayUseCase(uow)

    with pytest.raises(BusinessRuleViolation):
        use_case.execute(TaskId())
