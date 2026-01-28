"""UC-029: Manual Schedule Override use case."""
from datetime import datetime, UTC
from typing import Optional
from uuid import UUID

from app.domain.models.task import Task
from app.domain.models.enums import ScheduleChangeReason
from app.domain.models.schedule_history import ScheduleHistory
from app.application.ports.task_repository import TaskRepository
from app.application.ports.schedule_history_repository import ScheduleHistoryRepository
from app.application.ports.task_dependency_repository import TaskDependencyRepository
from app.application.ports.event_bus import EventBus
from app.application.services.schedule_service import ScheduleService
from app.application.events.domain_events import ScheduleOverridden
from app.domain.exceptions import BusinessRuleViolation


class OverrideTaskScheduleUseCase:
    """Use case for manually overriding a task schedule (UC-029)."""

    def __init__(
        self,
        task_repository: TaskRepository,
        schedule_history_repository: ScheduleHistoryRepository,
        task_dependency_repository: TaskDependencyRepository,
        event_bus: EventBus,
    ) -> None:
        self.task_repository = task_repository
        self.schedule_history_repository = schedule_history_repository
        self.task_dependency_repository = task_dependency_repository
        self.event_bus = event_bus

    def execute(
        self,
        task_id: UUID,
        new_expected_start: Optional[datetime],
        new_expected_end: Optional[datetime],
        reason: ScheduleChangeReason,
        changed_by_user_id: UUID,
    ) -> Task:
        """
        Override expected dates of a task.

        Flow:
        1. Load task
        2. Update expected dates
        3. Create ScheduleHistory with MANUAL_OVERRIDE (or provided reason)
        4. Emit ScheduleOverridden event
        5. Recalculate dependents via ScheduleService
        """
        task = self.task_repository.find_by_id(task_id)
        if task is None:
            raise BusinessRuleViolation(
                f"Task with id {task_id} not found",
                code="task_not_found",
            )

        old_expected_start = task.expected_start_date
        old_expected_end = task.expected_end_date

        task.expected_start_date = new_expected_start
        task.expected_end_date = new_expected_end
        self.task_repository.save(task)

        history = ScheduleHistory.create(
            task_id=task.id,
            old_expected_start=old_expected_start,
            old_expected_end=old_expected_end,
            new_expected_start=new_expected_start,
            new_expected_end=new_expected_end,
            reason=reason,
            caused_by_task_id=None,
            changed_by_user_id=changed_by_user_id,
        )
        self.schedule_history_repository.save(history)

        self.event_bus.emit(
            ScheduleOverridden(
                task_id=task.id,
                old_expected_start=old_expected_start,
                old_expected_end=old_expected_end,
                new_expected_start=new_expected_start,
                new_expected_end=new_expected_end,
                changed_by_user_id=changed_by_user_id,
                timestamp=datetime.now(UTC),
            )
        )

        # Recalculate dependents after manual override
        schedule_service = ScheduleService(
            task_repository=self.task_repository,
            task_dependency_repository=self.task_dependency_repository,
            schedule_history_repository=self.schedule_history_repository,
            event_bus=self.event_bus,
        )
        schedule_service.propagate_delay(task)

        return task

