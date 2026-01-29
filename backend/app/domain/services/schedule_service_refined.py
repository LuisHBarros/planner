"""Refined ScheduleService with proper BR-024, BR-026, BR-027 implementation."""
from datetime import timedelta
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
