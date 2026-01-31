"""Tests for Task entity."""
import pytest

from app.domain.models.task import Task
from app.domain.models.value_objects import ProjectId
from app.domain.models.enums import TaskStatus
from app.domain.exceptions import BusinessRuleViolation


def test_task_create_defaults_to_todo():
    """Task.create sets TODO status."""
    task = Task.create(
        project_id=ProjectId(),
        title="Build API",
    )
    assert task.status == TaskStatus.TODO
    assert task.title == "Build API"


def test_task_transition_invalid_raises():
    """Invalid status transitions raise error."""
    task = Task.create(project_id=ProjectId(), title="Test")
    with pytest.raises(BusinessRuleViolation):
        task.transition_to(TaskStatus.DONE)
