"""ScheduleService: handles schedule-aware logic and propagation (Spec 2.0).

This service implements:
- BR-023: Delay detection (actual_end > expected_end)
- BR-024: Cascading delay propagation
- BR-025: Historical integrity (ScheduleHistory is immutable)
- BR-026: Respect task lifecycle when propagating delays
- BR-027: Automatic delay detection timing
"""
from datetime import datetime
from datetime import UTC
from typing import List, Union
from uuid import UUID

from app.domain.models.task import Task
from app.domain.models.schedule_history import ScheduleHistory
from app.domain.models.enums import ScheduleChangeReason, TaskStatus
from app.domain.models.value_objects import TaskId
from app.application.ports.task_repository import TaskRepository
from app.application.ports.task_dependency_repository import TaskDependencyRepository
from app.application.ports.schedule_history_repository import ScheduleHistoryRepository
from app.application.ports.event_bus import EventBus
from app.application.events.domain_events import TaskDelayed, ScheduleChanged


class ScheduleService:
    """Application service for schedule calculations and delay propagation.

    This service orchestrates schedule-related operations, including:
    - Detecting delays when tasks complete (BR-023)
    - Propagating delays through dependency chains (BR-024)
    - Recording schedule changes for auditability (BR-025)
    - Respecting task lifecycle during propagation (BR-026)

    Responsibilities (Spec 2.0):
    - detect_delay(task): Check if task is delayed and emit events
    - propagate_delay(task): Cascade delays through dependency graph
    - handle_task_completed(task): Convenience entry point for UC-027/UC-028

    Note: This is an APPLICATION service (uses repositories, emits events).
    For pure domain logic without side effects, see domain/services/schedule_service_refined.py.
    """

    def __init__(
        self,
        task_repository: TaskRepository,
        task_dependency_repository: TaskDependencyRepository,
        schedule_history_repository: ScheduleHistoryRepository,
        event_bus: EventBus,
    ) -> None:
        """Initialize ScheduleService with required dependencies.

        Args:
            task_repository: Repository for task persistence
            task_dependency_repository: Repository for dependency queries
            schedule_history_repository: Repository for schedule history records
            event_bus: Event bus for emitting domain events
        """
        self.task_repository = task_repository
        self.task_dependency_repository = task_dependency_repository
        self.schedule_history_repository = schedule_history_repository
        self.event_bus = event_bus

    def detect_delay(self, task: Task) -> bool:
        """Detect if a task is delayed and mark it as such (BR-023).

        A task is considered delayed when actual_end_date > expected_end_date.
        This check should be called when a task transitions to DONE status.

        Args:
            task: The task to check for delay

        Returns:
            True if the task is delayed, False otherwise

        Side Effects:
            - Updates task.is_delayed flag
            - Persists the task via repository
            - Emits TaskDelayed event
        """
        if task.actual_end_date is None or task.expected_end_date is None:
            return False

        if task.actual_end_date <= task.expected_end_date:
            return False

        if task.is_delayed:
            # Already marked as delayed - idempotent
            return True

        task.is_delayed = True
        self.task_repository.save(task)

        # Emit TaskDelayed event for listeners
        self.event_bus.emit(
            TaskDelayed(
                task_id=task.id,
                delay_seconds=int(
                    (task.actual_end_date - task.expected_end_date).total_seconds()
                ),
                timestamp=datetime.now(UTC),
            )
        )

        return True

    def propagate_delay(self, root_task: Task) -> None:
        """Propagate delay from a root task through its dependent tasks (BR-024, BR-026).

        This method implements a BFS traversal of the dependency graph, shifting
        expected dates for all transitively dependent tasks.

        Algorithm:
        1. Calculate delay_delta = actual_end_date - expected_end_date
        2. BFS traverse all dependent tasks
        3. For each dependent task:
           - BR-025: Skip if status is DONE (completed tasks are immutable)
           - BR-026: If actual_start_date is set, only shift expected_end_date
           - Otherwise, shift both expected_start_date and expected_end_date
        4. For each shifted task, create ScheduleHistory and emit ScheduleChanged

        Args:
            root_task: The task that was delayed (already completed)

        Side Effects:
            - Updates expected dates for all affected dependent tasks
            - Creates ScheduleHistory records for audit trail
            - Emits ScheduleChanged events for each affected task
        """
        if root_task.actual_end_date is None or root_task.expected_end_date is None:
            return

        delay_delta = root_task.actual_end_date - root_task.expected_end_date
        if delay_delta.total_seconds() <= 0:
            return

        visited: set[TaskId] = set()
        queue: List[TaskId] = [root_task.id]

        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue
            visited.add(current_id)

            dependents = self.task_repository.find_dependent_tasks(current_id)
            for dependent in dependents:
                # BR-025: Skip completed tasks - actual dates are immutable
                if dependent.status == TaskStatus.DONE:
                    continue

                queue.append(dependent.id)

                old_expected_start = dependent.expected_start_date
                old_expected_end = dependent.expected_end_date

                # BR-026: Respect task lifecycle
                if dependent.actual_start_date is not None:
                    # Task already started - only shift end date
                    # Start date cannot change (already happened)
                    if dependent.expected_end_date is not None:
                        dependent.expected_end_date = dependent.expected_end_date + delay_delta
                else:
                    # Task not started - shift both dates
                    if dependent.expected_start_date is not None:
                        dependent.expected_start_date = dependent.expected_start_date + delay_delta
                    if dependent.expected_end_date is not None:
                        dependent.expected_end_date = dependent.expected_end_date + delay_delta

                # Persist only if something changed
                if (
                    dependent.expected_start_date != old_expected_start
                    or dependent.expected_end_date != old_expected_end
                ):
                    self.task_repository.save(dependent)

                    # BR-025: Create immutable history record
                    history = ScheduleHistory.create(
                        task_id=dependent.id,
                        old_expected_start=old_expected_start,
                        old_expected_end=old_expected_end,
                        new_expected_start=dependent.expected_start_date,
                        new_expected_end=dependent.expected_end_date,
                        reason=ScheduleChangeReason.DEPENDENCY_DELAY,
                        caused_by_task_id=current_id,
                        changed_by_user_id=None,
                    )
                    self.schedule_history_repository.save(history)

                    # Emit ScheduleChanged event for listeners
                    self.event_bus.emit(
                        ScheduleChanged(
                            task_id=dependent.id,
                            old_expected_start=old_expected_start,
                            old_expected_end=old_expected_end,
                            new_expected_start=dependent.expected_start_date,
                            new_expected_end=dependent.expected_end_date,
                            caused_by_task_id=current_id,
                            timestamp=datetime.now(UTC),
                        )
                    )

    def handle_task_completed(self, task: Task) -> None:
        """Entry point for automatic delay handling when task completes (BR-027).

        This is the main entry point called when a task transitions to DONE status.
        It automatically:
        1. Checks if the task is delayed (actual_end > expected_end)
        2. If delayed, propagates the delay through all dependent tasks

        Args:
            task: The task that just completed

        Side Effects:
            - May mark task as delayed
            - May update dependent tasks' expected dates
            - May create ScheduleHistory records
            - May emit TaskDelayed and ScheduleChanged events
        """
        if self.detect_delay(task):
            self.propagate_delay(task)

