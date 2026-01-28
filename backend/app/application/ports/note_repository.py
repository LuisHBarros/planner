"""Note repository port."""
from typing import Protocol, Optional, List
from uuid import UUID
from app.domain.models.note import Note


class NoteRepository(Protocol):
    """Repository interface for Note entities."""
    
    def save(self, note: Note) -> None:
        """Save a note."""
        ...
    
    def find_by_id(self, note_id: UUID) -> Optional[Note]:
        """Find note by ID."""
        ...
    
    def find_by_task_id(self, task_id: UUID) -> List[Note]:
        """Find all notes for a task, ordered by created_at."""
        ...
