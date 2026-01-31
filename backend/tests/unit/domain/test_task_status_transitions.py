"""Tests for task status transitions."""
from app.domain.models.task import Task, VALID_TRANSITIONS
from app.domain.models.enums import TaskStatus
from app.domain.models.value_objects import ProjectId


def test_valid_transitions_map():
    """Transition map contains expected keys."""
    assert TaskStatus.TODO in VALID_TRANSITIONS
    assert TaskStatus.DONE in VALID_TRANSITIONS


def test_can_transition_to():
    """Task.can_transition_to respects map."""
    task = Task.create(project_id=ProjectId(), title="A")
    assert task.can_transition_to(TaskStatus.DOING) is True
    assert task.can_transition_to(TaskStatus.DONE) is False
