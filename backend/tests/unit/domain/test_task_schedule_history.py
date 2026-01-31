"""Tests for TaskScheduleHistory entity."""
from app.domain.models.task_schedule_history import TaskScheduleHistory
from app.domain.models.enums import ScheduleChangeReason
from app.domain.models.value_objects import TaskId, UtcDateTime


def test_task_schedule_history_create():
    """TaskScheduleHistory.create stores reason."""
    history = TaskScheduleHistory.create(
        task_id=TaskId(),
        previous_start=UtcDateTime(),
        previous_end=UtcDateTime(),
        new_start=UtcDateTime(),
        new_end=UtcDateTime(),
        reason=ScheduleChangeReason.DEPENDENCY_DELAY,
    )
    assert history.reason == ScheduleChangeReason.DEPENDENCY_DELAY
