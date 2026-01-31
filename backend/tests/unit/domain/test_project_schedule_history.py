"""Tests for ProjectScheduleHistory entity."""
from app.domain.models.project_schedule_history import ProjectScheduleHistory
from app.domain.models.enums import ScheduleChangeReason
from app.domain.models.value_objects import ProjectId, UtcDateTime


def test_project_schedule_history_create():
    """ProjectScheduleHistory.create stores reason."""
    history = ProjectScheduleHistory.create(
        project_id=ProjectId(),
        previous_end=UtcDateTime(),
        new_end=UtcDateTime(),
        reason=ScheduleChangeReason.MANUAL_OVERRIDE,
    )
    assert history.reason == ScheduleChangeReason.MANUAL_OVERRIDE
