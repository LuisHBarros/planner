"""ScheduleService: handles schedule-aware logic and propagation (Spec 2.0)."""
from datetime import datetime
from datetime import UTC
from typing import Optional, List
from uuid import UUID

from app.domain.models.task import Task
from app.domain.models.schedule_history import ScheduleHistory
from app.domain.models.enums import ScheduleChangeReason
from app.application.ports.task_repository import TaskRepository
from app.application.ports.task_dependency_repository import TaskDependencyRepository
from app.application.ports.schedule_history_repository import ScheduleHistoryRepository
from app.application.ports.event_bus import EventBus
from app.application.events.domain_events import TaskDelayed, ScheduleChanged


class ScheduleService:
    """
    Service responsible for schedule calculations and propagation.

    Responsibilities (Spec 2.0):
    - detect_delay(task)
    - propagate_delay(task)
    - recalculate_dependents(task)
    """

    def __init__(
        self,
        task_repository: TaskRepository,
        task_dependency_repository: TaskDependencyRepository,
        schedule_history_repository: ScheduleHistoryRepository,
        event_bus: EventBus,
    ) -> None:
        self.task_repository = task_repository
        self.task_dependency_repository = task_dependency_repository
        self.schedule_history_repository = schedule_history_repository
        self.event_bus = event_bus

    def detect_delay(self, task: Task) -> bool:
        """
        Detect if a task is delayed and mark it as such.

        Returns True if the task is delayed according to Spec 2.0:
        actual_end_date > expected_end_date.
        """
        if task.actual_end_date is None or task.expected_end_date is None:
            return False

        if task.actual_end_date <= task.expected_end_date:
            return False

        if task.is_delayed:
            # Already marked as delayed
            return True

        task.is_delayed = True
        self.task_repository.save(task)

        # Emit TaskDelayed event
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
        """
        Propagate delay from a root task through its dependent tasks.

        Strategy:
        - Compute delay delta from expected_end_date to actual_end_date.
        - For each dependent task (transitively), shift expected_start_date and
          expected_end_date by the same delta.
        - For each affected task, create ScheduleHistory and emit ScheduleChanged.
        """
        if root_task.actual_end_date is None or root_task.expected_end_date is None:
            return

        delay_delta = root_task.actual_end_date - root_task.expected_end_date
        if delay_delta.total_seconds() <= 0:
            return

        visited: set[UUID] = set()
        queue: List[UUID] = [root_task.id]

        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue
            visited.add(current_id)

            dependents = self.task_repository.find_dependent_tasks(current_id)
            for dependent in dependents:
                queue.append(dependent.id)

                old_expected_start = dependent.expected_start_date
                old_expected_end = dependent.expected_end_date

                # Shift expected dates if they exist
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

                    # Emit ScheduleChanged event
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
        """
        Convenience entry point for UC-027 & UC-028:
        1) Detect delay when task is completed.
        2) If delayed, propagate schedule changes.
        """
        if self.detect_delay(task):
            self.propagate_delay(task)

