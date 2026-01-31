"""Tests for schedule calculator."""
from datetime import datetime, timedelta, timezone

from app.domain.models.task import Task
from app.domain.models.enums import TaskStatus
from app.domain.models.value_objects import ProjectId, UtcDateTime
from app.domain.services.schedule_calculator import (
    calculate_delay_delta,
    calculate_max_delay_from_parents,
    calculate_new_dates,
    detect_delay,
)


def test_detect_delay_true_when_actual_after_expected():
    """detect_delay is True for delayed tasks."""
    task = Task.create(project_id=ProjectId(), title="A")
    task.expected_end_date = UtcDateTime(datetime(2024, 1, 1, tzinfo=timezone.utc))
    task.actual_end_date = UtcDateTime(datetime(2024, 1, 2, tzinfo=timezone.utc))
    assert detect_delay(task) is True


def test_calculate_delay_delta():
    """Delay delta reflects actual - expected."""
    task = Task.create(project_id=ProjectId(), title="A")
    task.expected_end_date = UtcDateTime(datetime(2024, 1, 1, tzinfo=timezone.utc))
    task.actual_end_date = UtcDateTime(datetime(2024, 1, 3, tzinfo=timezone.utc))
    assert calculate_delay_delta(task) == timedelta(days=2)


def test_calculate_max_delay_from_parents_uses_done_actual():
    """Done parents use actual_end_date if available."""
    parent = Task.create(project_id=ProjectId(), title="A")
    parent.status = TaskStatus.DONE
    parent.actual_end_date = UtcDateTime(datetime(2024, 1, 5, tzinfo=timezone.utc))
    max_date = calculate_max_delay_from_parents([parent])
    assert max_date == parent.actual_end_date


def test_calculate_new_dates_shifts_not_started():
    """Unstarted tasks shift both start and end."""
    task = Task.create(project_id=ProjectId(), title="A")
    task.expected_start_date = UtcDateTime(datetime(2024, 1, 1, tzinfo=timezone.utc))
    task.expected_end_date = UtcDateTime(datetime(2024, 1, 2, tzinfo=timezone.utc))
    new_start, new_end = calculate_new_dates(task, timedelta(days=1))
    assert new_start.value == datetime(2024, 1, 2, tzinfo=timezone.utc)
    assert new_end.value == datetime(2024, 1, 3, tzinfo=timezone.utc)
