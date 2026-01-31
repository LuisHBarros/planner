"""Tests for TaskAbandonment entity."""
from app.domain.models.task_abandonment import TaskAbandonment
from app.domain.models.enums import AbandonmentType
from app.domain.models.value_objects import TaskId, UserId


def test_task_abandonment_create():
    """TaskAbandonment.create stores type."""
    record = TaskAbandonment.create(
        task_id=TaskId(),
        user_id=UserId(),
        abandonment_type=AbandonmentType.VOLUNTARY,
        note="Reason",
    )
    assert record.abandonment_type == AbandonmentType.VOLUNTARY
    assert record.note == "Reason"
