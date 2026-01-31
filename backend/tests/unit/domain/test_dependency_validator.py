"""Tests for dependency validator."""
from app.domain.models.value_objects import TaskId
from app.domain.services.dependency_validator import detect_cycle


def test_detect_cycle_self_dependency():
    """Self-dependency is a cycle."""
    task_id = TaskId()
    assert detect_cycle(task_id, task_id, {}) is True


def test_detect_cycle_detects_indirect_cycle():
    """Cycle detected through dependency chain."""
    a = TaskId()
    b = TaskId()
    c = TaskId()
    existing = {b: [c], c: [a]}
    assert detect_cycle(a, b, existing) is True


def test_detect_cycle_no_cycle():
    """No cycle when dependencies don't reach task."""
    a = TaskId()
    b = TaskId()
    existing = {b: []}
    assert detect_cycle(a, b, existing) is False
