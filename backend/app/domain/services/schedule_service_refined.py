"""Refined ScheduleService with proper BR-024, BR-026, BR-027, BR-SCHED implementation."""
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from uuid import UUID

from app.domain.models.task import Task
from app.domain.models.enums import TaskStatus


class ScheduleService:
    """
    Domain Service: Pure schedule calculation logic.

    Responsibilities:
    1. Detect delays (BR-023)
    2. Calculate delay delta
    3. Propagate delays with proper algorithms (BR-024, BR-026)
    4. Preserve invariants (duration, immutability)

    Does NOT persist, emit events, or have side effects.
    """

    def detect_delay(self, task: Task) -> bool:
        """
        Check if task is delayed (BR-023).

        Args:
            task: Task to check

        Returns:
            True if actual_end_date > expected_end_date
        """
        if task.actual_end_date is None or task.expected_end_date is None:
            return False

        return task.actual_end_date > task.expected_end_date

    def calculate_delay_delta(self, task: Task) -> Optional[timedelta]:
        """
        Calculate how many days task is delayed.

        Args:
            task: Task to analyze

        Returns:
            timedelta of delay, or None if not delayed
        """
        if not self.detect_delay(task):
            return None

        return task.actual_end_date - task.expected_end_date

    def propagate_delay_to_dependents(
        self,
        task: Task,
        dependents: List[Task],
    ) -> List[Task]:
        """
        Calculate new expected dates for dependent tasks (BR-024, BR-026).

        Algorithm:
        1. Calculate delay_delta
        2. For each dependent:
           a. If status = DONE: skip (immutable actual date)
           b. If actual_start_date is set:
              - Preserve expected_start (already started)
              - Shift expected_end
           c. Else: Shift both expected_start and expected_end
        3. Preserve duration invariant

        Args:
            task: Root task that is delayed
            dependents: All tasks that depend on task

        Returns:
            List of updated tasks (NOT persisted, caller must persist)
        """
        delay_delta = self.calculate_delay_delta(task)
        if delay_delta is None or delay_delta.total_seconds() <= 0:
            return []

        updated = []

        for dependent in dependents:
            # BR-025: Don't propagate to completed tasks (immutable actual date)
            if dependent.status == TaskStatus.DONE:
                continue

            # BR-026: Respect task lifecycle
            if dependent.actual_start_date is not None:
                # Task already started - only shift end date
                # Preserve expected_start (already happened in reality)
                if dependent.expected_end_date is not None:
                    old_expected_end = dependent.expected_end_date
                    dependent.expected_end_date = old_expected_end + delay_delta
                    # Track change for caller
                    dependent._was_shifted = True  # noqa: SLF001
            else:
                # Task not started - shift both dates
                # Future is flexible, can reschedule
                if dependent.expected_start_date is not None:
                    dependent.expected_start_date = (
                        dependent.expected_start_date + delay_delta
                    )

                if dependent.expected_end_date is not None:
                    dependent.expected_end_date = (
                        dependent.expected_end_date + delay_delta
                    )

                # Track change for caller
                dependent._was_shifted = True  # noqa: SLF001

            updated.append(dependent)

        return updated

    def calculate_max_delay_from_paths(
        self,
        delays_per_path: Dict[UUID, timedelta],
    ) -> timedelta:
        """
        Calculate maximum delay when multiple paths exist (BR-024).

        If A → D (delays 2 days) and B → D (delays 4 days):
        Result: max(2, 4) = 4 days

        Args:
            delays_per_path: Dict of {source_task_id: delay_delta}

        Returns:
            Maximum delay (using algebraic comparison)
        """
        if not delays_per_path:
            return timedelta(0)

        max_delay = max(delays_per_path.values(), key=lambda d: d.total_seconds())
        return max_delay

    def calculate_expected_start_from_parents(
        self,
        task: Task,
        parent_tasks: List[Task],
    ) -> Optional[datetime]:
        """
        Calculate expected start date based on parent tasks (BR-SCHED-002/003).

        The MAX rule: new_expected_start = MAX(actual_end OR expected_end of all parents) + 1 day

        When a task has multiple dependencies, it cannot start until ALL parents
        are complete. This method calculates the earliest possible start date
        based on when the latest parent will finish.

        Args:
            task: The task whose expected start to calculate
            parent_tasks: All tasks that this task depends on

        Returns:
            The calculated expected start date, or None if no parents have dates
        """
        if not parent_tasks:
            return None

        max_end_date: Optional[datetime] = None

        for parent in parent_tasks:
            # Use actual_end_date if complete, otherwise expected_end_date
            parent_end = parent.actual_end_date or parent.expected_end_date

            if parent_end is None:
                continue

            if max_end_date is None or parent_end > max_end_date:
                max_end_date = parent_end

        if max_end_date is None:
            return None

        # Add 1 day buffer (start the day after the last parent finishes)
        return max_end_date + timedelta(days=1)

    def update_expected_dates_from_parents(
        self,
        task: Task,
        parent_tasks: List[Task],
    ) -> bool:
        """
        Update task's expected dates based on parent completion (BR-SCHED-002/003).

        This method:
        1. Calculates new expected_start using MAX rule
        2. Preserves duration (shifts expected_end accordingly)
        3. Returns whether task was updated

        Args:
            task: The task to update
            parent_tasks: All tasks that this task depends on

        Returns:
            True if task dates were updated, False otherwise
        """
        # Don't update completed or cancelled tasks
        if task.status in [TaskStatus.DONE, TaskStatus.CANCELLED]:
            return False

        new_start = self.calculate_expected_start_from_parents(task, parent_tasks)

        if new_start is None:
            return False

        # Only update if the new start is later than current
        if task.expected_start_date is not None and new_start <= task.expected_start_date:
            return False

        # Calculate current duration to preserve it
        duration: Optional[timedelta] = None
        if task.expected_start_date is not None and task.expected_end_date is not None:
            duration = task.expected_end_date - task.expected_start_date

        # Update start date
        old_start = task.expected_start_date
        task.expected_start_date = new_start

        # Preserve duration by shifting end date
        if duration is not None:
            task.expected_end_date = new_start + duration
        elif task.expected_end_date is not None and old_start is not None:
            # If we had an end date but no start, shift end by the same delta
            delta = new_start - old_start
            task.expected_end_date = task.expected_end_date + delta

        return True
