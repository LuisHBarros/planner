"""UC-023: Update Task Progress (Manual) use case."""
from datetime import datetime, UTC
from uuid import UUID

from app.domain.models.task import Task
from app.domain.models.note import Note
from app.application.ports.task_repository import TaskRepository
from app.application.ports.note_repository import NoteRepository
from app.application.ports.event_bus import EventBus
from app.application.events.domain_events import TaskProgressUpdated
from app.domain.exceptions import BusinessRuleViolation


class UpdateTaskProgressManualUseCase:
    """Use case for manually updating task progress (UC-023)."""
    
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
        completion_percentage: int,
        user_id: UUID,
    ) -> Task:
        """
        Manually update task progress.
        
        Flow:
        1. Load task
        2. Validate percentage (0-100)
        3. Validate task is not done
        4. Set manual progress (domain method validates BR-018)
        5. Emit TaskProgressUpdated event
        6. Create note
        7. Return updated task
        """
        # Load task
        task = self.task_repository.find_by_id(task_id)
        if task is None:
            raise BusinessRuleViolation(
                f"Task with id {task_id} not found",
                code="task_not_found"
            )
        
        # Set manual progress (domain method validates BR-018)
        task.set_manual_progress(completion_percentage)
        
        # Save
        self.task_repository.save(task)
        
        # Emit event
        from app.domain.models.enums import CompletionSource

        self.event_bus.emit(
            TaskProgressUpdated(
                task_id=task_id,
                completion_percentage=completion_percentage,
                source=CompletionSource.MANUAL,
                reasoning=None,
                timestamp=datetime.now(UTC),
                user_id=user_id,
            )
        )
        
        # Create note
        note = Note.create_system_note(
            task_id=task_id,
            content=f"Progress updated to {completion_percentage}% by user {user_id}",
        )
        self.note_repository.save(note)
        
        return task
