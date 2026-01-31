"""Schedule calculator per BR-SCHED."""
from datetime import timedelta
from typing import List, Optional

from app.domain.models.task import Task
from app.domain.models.value_objects import UtcDateTime
from app.domain.models.enums import TaskStatus


def detect_delay(task: Task) -> bool:
    """Detect if task is delayed (BR-SCHED-001)."""
    if task.actual_end_date is None or task.expected_end_date is None:
        return False
    return task.actual_end_date > task.expected_end_date


def calculate_delay_delta(task: Task) -> Optional[timedelta]:
    """Calculate delay amount."""
    if task.actual_end_date is None or task.expected_end_date is None:
        return None
    return task.actual_end_date.value - task.expected_end_date.value


def calculate_max_delay_from_parents(
    parent_tasks: List[Task],
) -> Optional[UtcDateTime]:
    """
    Calculate the maximum end date from parent tasks (BR-SCHED-003).

    Uses actual_end_date if task is DONE, otherwise expected_end_date.
    """
    if not parent_tasks:
        return None

    max_date = None
    for parent in parent_tasks:
        if parent.status == TaskStatus.DONE and parent.actual_end_date:
            parent_end = parent.actual_end_date
        elif parent.expected_end_date:
            parent_end = parent.expected_end_date
        else:
            continue

        if max_date is None or parent_end > max_date:
            max_date = parent_end

    return max_date


def calculate_new_dates(
    task: Task,
    delay_delta: timedelta,
) -> tuple[Optional[UtcDateTime], Optional[UtcDateTime]]:
    """
    Calculate new expected dates respecting task lifecycle (BR-SCHED-005).

    - If DONE: skip (immutable)
    - If started (actual_start_date set): only shift expected_end
    - If not started: shift both
    """
    if task.status == TaskStatus.DONE:
        return task.expected_start_date, task.expected_end_date

    new_start = task.expected_start_date
    new_end = task.expected_end_date

    if task.actual_start_date is not None:
        # Task started - only shift end (BR-SCHED-005)
        if task.expected_end_date:
            new_end = UtcDateTime(task.expected_end_date.value + delay_delta)
    else:
        # Task not started - shift both
        if task.expected_start_date:
            new_start = UtcDateTime(task.expected_start_date.value + delay_delta)
        if task.expected_end_date:
            new_end = UtcDateTime(task.expected_end_date.value + delay_delta)

    return new_start, new_end
