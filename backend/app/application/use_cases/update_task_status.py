"""UC-007: Update Task Status use case (v3.0 with CANCELLED support)."""
from datetime import datetime, UTC
from uuid import UUID
from typing import Optional

from app.domain.models.task import Task
from app.domain.models.note import Note
from app.domain.models.task_assignment_history import TaskAssignmentHistory
from app.domain.models.enums import TaskStatus, AssignmentAction
from app.application.ports.task_repository import TaskRepository
from app.application.ports.note_repository import NoteRepository
from app.application.ports.task_assignment_history_repository import TaskAssignmentHistoryRepository
from app.application.ports.event_bus import EventBus
from app.application.events.domain_events import TaskStatusChanged, TaskCompleted
from app.application.services.schedule_service import ScheduleService
from app.domain.exceptions import BusinessRuleViolation


class UpdateTaskStatusUseCase:
    """Use case for updating task status (UC-007, v3.0)."""

    def __init__(
        self,
        task_repository: TaskRepository,
        note_repository: NoteRepository,
        event_bus: EventBus,
        schedule_service: Optional[ScheduleService] = None,
        task_assignment_history_repository: Optional[TaskAssignmentHistoryRepository] = None,
    ):
        self.task_repository = task_repository
        self.note_repository = note_repository
        self.event_bus = event_bus
        self.schedule_service = schedule_service
        self.task_assignment_history_repository = task_assignment_history_repository

    def execute(
        self,
        task_id: UUID,
        new_status: TaskStatus,
        user_id: Optional[UUID] = None,
    ) -> Task:
        """
        Update task status.

        Flow:
        1. Load task
        2. Validate status transition (BR-007, v3.0)
        3. Update status (domain method)
        4. Update timestamps
        5. Record assignment history if applicable
        6. Emit TaskStatusChanged event
        7. If done, emit TaskCompleted event and trigger schedule propagation
        8. Create note
        9. Return updated task
        """
        # Load task
        task = self.task_repository.find_by_id(task_id)
        if task is None:
            raise BusinessRuleViolation(
                f"Task with id {task_id} not found",
                code="task_not_found"
            )

        old_status = task.status
        old_user_id = task.user_responsible_id

        # Update status (domain method validates BR-006, BR-007, v3.0 CANCELLED)
        task.update_status(new_status)

        # Save
        self.task_repository.save(task)

        # v3.0: Record assignment history for status changes
        if self.task_assignment_history_repository is not None:
            # Record completion
            if new_status == TaskStatus.DONE and old_user_id is not None:
                history = TaskAssignmentHistory.record_completed(
                    task_id=task.id,
                    user_id=old_user_id,
                )
                self.task_assignment_history_repository.save(history)

        # Emit TaskStatusChanged event
        self.event_bus.emit(
            TaskStatusChanged(
                task_id=task.id,
                old_status=old_status,
                new_status=new_status,
                timestamp=datetime.now(UTC),
                user_id=user_id,
            )
        )

        # If done, emit TaskCompleted event
        if new_status == TaskStatus.DONE:
            lead_time_days = 0.0
            if task.completed_at and task.created_at:
                delta = task.completed_at - task.created_at
                lead_time_days = delta.total_seconds() / (24 * 3600)

            self.event_bus.emit(
                TaskCompleted(
                    task_id=task.id,
                    completed_by=user_id or task.id,
                    lead_time_days=lead_time_days,
                    timestamp=datetime.now(UTC),
                    user_id=user_id,
                )
            )

            # UC-027 / UC-028: detect delay and propagate schedule changes
            if self.schedule_service is not None:
                self.schedule_service.handle_task_completed(task)

        # Create note
        note = Note.create_system_note(
            task_id=task.id,
            content=f"Status changed from {old_status.value} to {new_status.value}",
        )
        self.note_repository.save(note)

        return task
