"""UC-008: Add Task Note use case."""
from datetime import datetime, UTC
from uuid import UUID

from app.domain.models.note import Note
from app.domain.models.enums import NoteType
from app.application.ports.note_repository import NoteRepository
from app.application.ports.task_repository import TaskRepository
from app.application.ports.event_bus import EventBus
from app.application.events.domain_events import NoteAdded
from app.domain.exceptions import BusinessRuleViolation


class AddTaskNoteUseCase:
    """Use case for adding a task note (UC-008)."""
    
    def __init__(
        self,
        note_repository: NoteRepository,
        task_repository: TaskRepository,
        event_bus: EventBus,
    ):
        self.note_repository = note_repository
        self.task_repository = task_repository
        self.event_bus = event_bus
    
    def execute(
        self,
        task_id: UUID,
        content: str,
        author_id: UUID,
    ) -> Note:
        """
        Add a note to a task.
        
        Flow:
        1. Validate task exists
        2. Create note
        3. Save note
        4. Emit NoteAdded event
        5. Return note
        """
        # Validate task exists
        task = self.task_repository.find_by_id(task_id)
        if task is None:
            raise BusinessRuleViolation(
                f"Task with id {task_id} not found",
                code="task_not_found"
            )
        
        # Create note
        note = Note.create(
            task_id=task_id,
            content=content,
            author_id=author_id,
            note_type=NoteType.COMMENT,
        )
        
        # Save
        self.note_repository.save(note)
        
        # Emit event
        self.event_bus.emit(
            NoteAdded(
                task_id=task_id,
                note_id=note.id,
                author_id=author_id,
                timestamp=datetime.now(UTC),
                user_id=author_id,
            )
        )
        
        return note
