"""Workload calculator per BR-WORK."""
from typing import List

from app.domain.models.task import Task
from app.domain.models.enums import MemberLevel, WorkloadStatus, TaskStatus

# BR-WORK-001: Level multipliers
LEVEL_MULTIPLIERS = {
    MemberLevel.JUNIOR: 0.6,
    MemberLevel.MID: 1.0,
    MemberLevel.SENIOR: 1.3,
    MemberLevel.SPECIALIST: 1.2,
    MemberLevel.LEAD: 1.1,
}


def calculate_workload_score(tasks: List[Task]) -> int:
    """Calculate total workload from DOING tasks."""
    return sum(
        task.difficulty or 0
        for task in tasks
        if task.status == TaskStatus.DOING
    )


def calculate_capacity(base_capacity: int, level: MemberLevel) -> float:
    """Calculate effective capacity based on level."""
    return base_capacity * LEVEL_MULTIPLIERS.get(level, 1.0)


def calculate_workload_status(
    workload_score: int,
    capacity: float,
) -> WorkloadStatus:
    """Determine workload status per BR-WORK-002."""
    if capacity == 0:
        return WorkloadStatus.IDLE

    ratio = workload_score / capacity

    if ratio > 1.5:
        return WorkloadStatus.IMPOSSIBLE
    if ratio > 1.2:
        return WorkloadStatus.TIGHT
    if ratio > 0.7:
        return WorkloadStatus.HEALTHY
    if ratio > 0.3:
        return WorkloadStatus.RELAXED
    return WorkloadStatus.IDLE


def would_be_impossible(
    current_tasks: List[Task],
    new_task: Task,
    base_capacity: int,
    level: MemberLevel,
) -> bool:
    """Check if adding new_task would result in IMPOSSIBLE status (BR-ASSIGN-003)."""
    current_score = calculate_workload_score(current_tasks)
    new_score = current_score + (new_task.difficulty or 0)
    capacity = calculate_capacity(base_capacity, level)
    status = calculate_workload_status(new_score, capacity)
    return status == WorkloadStatus.IMPOSSIBLE
