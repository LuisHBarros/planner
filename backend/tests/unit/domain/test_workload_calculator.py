"""Tests for workload calculator."""
from app.domain.models.task import Task
from app.domain.models.enums import MemberLevel, TaskStatus, WorkloadStatus
from app.domain.models.value_objects import ProjectId
from app.domain.services.workload_calculator import (
    calculate_capacity,
    calculate_workload_score,
    calculate_workload_status,
    would_be_impossible,
)


def test_calculate_workload_score_uses_doing_tasks():
    """Only DOING tasks count toward workload."""
    doing = Task.create(project_id=ProjectId(), title="A")
    doing.status = TaskStatus.DOING
    doing.difficulty = 3
    todo = Task.create(project_id=ProjectId(), title="B")
    todo.difficulty = 5
    assert calculate_workload_score([doing, todo]) == 3


def test_calculate_capacity_uses_multiplier():
    """Capacity scales by level."""
    assert calculate_capacity(10, MemberLevel.SENIOR) == 13.0


def test_calculate_workload_status_thresholds():
    """Status reflects ratio thresholds."""
    assert calculate_workload_status(16, 10) == WorkloadStatus.IMPOSSIBLE
    assert calculate_workload_status(13, 10) == WorkloadStatus.TIGHT
    assert calculate_workload_status(8, 10) == WorkloadStatus.HEALTHY
    assert calculate_workload_status(4, 10) == WorkloadStatus.RELAXED
    assert calculate_workload_status(2, 10) == WorkloadStatus.IDLE


def test_would_be_impossible_detects_overload():
    """Adding task should not exceed IMPOSSIBLE."""
    current = []
    new_task = Task.create(project_id=ProjectId(), title="A")
    new_task.difficulty = 20
    assert would_be_impossible(current, new_task, base_capacity=10, level=MemberLevel.MID)
