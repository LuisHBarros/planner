"""Tests for TaskAssignmentHistory entity."""
from app.domain.models.task_assignment_history import TaskAssignmentHistory
from app.domain.models.value_objects import TaskId, UserId


def test_task_assignment_history_create():
    """TaskAssignmentHistory.create sets fields."""
    history = TaskAssignmentHistory.create(
        task_id=TaskId(),
        user_id=UserId(),
        assignment_reason="auto",
    )
    assert history.unassigned_at is None
    assert history.assignment_reason == "auto"
