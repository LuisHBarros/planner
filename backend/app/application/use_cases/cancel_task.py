"""UC: Cancel Task use case (v3.0)."""
from datetime import datetime, UTC
from typing import Optional
from uuid import UUID

from app.domain.models.note import Note
from app.domain.models.task import Task
from app.domain.models.task_abandonment import TaskAbandonment
from app.domain.models.task_assignment_history import TaskAssignmentHistory
from app.domain.models.enums import AbandonmentType, TaskStatus
from app.application.ports.task_repository import TaskRepository
from app.application.ports.note_repository import NoteRepository
from app.application.ports.project_member_repository import ProjectMemberRepository
from app.application.ports.task_abandonment_repository import TaskAbandonmentRepository
from app.application.ports.task_assignment_history_repository import TaskAssignmentHistoryRepository
from app.application.ports.event_bus import EventBus
from app.application.events.domain_events import TaskCancelled
from app.domain.exceptions import BusinessRuleViolation


class CancelTaskUseCase:
    """
    Use case for cancelling a task (v3.0).

    Only managers can cancel tasks. If a task was in DOING status,
    a TaskAbandonment record with TASK_CANCELLED is created.
    """

    def __init__(
        self,
        task_repository: TaskRepository,
        note_repository: NoteRepository,
        project_member_repository: ProjectMemberRepository,
        task_abandonment_repository: TaskAbandonmentRepository,
        task_assignment_history_repository: TaskAssignmentHistoryRepository,
        event_bus: EventBus,
    ):
        self.task_repository = task_repository
        self.note_repository = note_repository
        self.project_member_repository = project_member_repository
        self.task_abandonment_repository = task_abandonment_repository
        self.task_assignment_history_repository = task_assignment_history_repository
        self.event_bus = event_bus

    def execute(
        self,
        task_id: UUID,
        cancelled_by_user_id: UUID,
        reason: Optional[str] = None,
    ) -> Task:
        """
        Cancel a task.

        Args:
            task_id: The task to cancel
            cancelled_by_user_id: The user cancelling the task (must be a manager)
            reason: Optional reason for cancellation

        Returns:
            The cancelled task
        """
        # Load task
        task = self.task_repository.find_by_id(task_id)
        if task is None:
            raise BusinessRuleViolation(
                f"Task with id {task_id} not found",
                code="task_not_found"
            )

        # Verify user is a manager in the project
        project_member = self.project_member_repository.find_by_project_and_user(
            project_id=task.project_id,
            user_id=cancelled_by_user_id,
        )

        if project_member is None:
            raise BusinessRuleViolation(
                "User is not a member of this project",
                code="not_project_member"
            )

        if not project_member.is_manager():
            raise BusinessRuleViolation(
                "Only managers can cancel tasks",
                code="not_manager"
            )

        # Remember if task was in DOING status with an assigned user
        was_in_progress = task.status == TaskStatus.DOING
        assigned_user_id = task.user_responsible_id

        # Cancel the task (domain method handles validation)
        task.cancel(reason)

        # Save task
        self.task_repository.save(task)

        # If task was in progress, create abandonment record
        if was_in_progress and assigned_user_id is not None:
            abandonment = TaskAbandonment.task_cancelled(
                task_id=task.id,
                user_id=assigned_user_id,
                cancelled_by_user_id=cancelled_by_user_id,
                reason=reason,
            )
            self.task_abandonment_repository.save(abandonment)

            # Record assignment history
            history = TaskAssignmentHistory.record_abandoned(
                task_id=task.id,
                user_id=assigned_user_id,
                abandonment_type=AbandonmentType.TASK_CANCELLED,
            )
            self.task_assignment_history_repository.save(history)

        # Emit event
        self.event_bus.emit(
            TaskCancelled(
                task_id=task.id,
                cancelled_by_user_id=cancelled_by_user_id,
                reason=reason,
                timestamp=datetime.now(UTC),
            )
        )

        # Create note
        note_content = "Task cancelled"
        if reason:
            note_content += f": {reason}"
        note = Note.create_system_note(
            task_id=task.id,
            content=note_content,
        )
        self.note_repository.save(note)

        return task
