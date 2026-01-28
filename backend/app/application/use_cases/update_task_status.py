"""UC-007: Update Task Status use case."""
from datetime import datetime, UTC
from uuid import UUID
from typing import Optional

from app.domain.models.task import Task
from app.domain.models.note import Note
from app.domain.models.enums import TaskStatus
from app.application.ports.task_repository import TaskRepository
from app.application.ports.note_repository import NoteRepository
from app.application.ports.event_bus import EventBus
from app.application.events.domain_events import TaskStatusChanged, TaskCompleted
from app.domain.exceptions import BusinessRuleViolation


class UpdateTaskStatusUseCase:
    """Use case for updating task status (UC-007)."""
    
    def __init__(
        self,
        task_repository: TaskRepository,
        note_repository: NoteRepository,
        event_bus: EventBus,
    ):
        self.task_repository = task_repository
        self.note_repository = note_repository
        self.event_bus = event_bus
    
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
        2. Validate status transition (BR-007)
        3. Update status (domain method)
        4. Update timestamps
        5. Emit TaskStatusChanged event
        6. If done, emit TaskCompleted event
        7. Create note
        8. Return updated task
        """
        # Load task
        task = self.task_repository.find_by_id(task_id)
        if task is None:
            raise BusinessRuleViolation(
                f"Task with id {task_id} not found",
                code="task_not_found"
            )
        
        old_status = task.status
        
        # Update status (domain method validates BR-006, BR-007)
        task.update_status(new_status)
        
        # Save
        self.task_repository.save(task)
        
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
        
        # Create note
        note = Note.create_system_note(
            task_id=task.id,
            content=f"Status changed from {old_status.value} to {new_status.value}",
        )
        self.note_repository.save(note)
        
        return task
