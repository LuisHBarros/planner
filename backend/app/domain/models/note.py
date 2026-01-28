"""Note domain model."""
from datetime import datetime, UTC
from typing import Optional
from uuid import UUID, uuid4

from app.domain.models.enums import NoteType


class Note:
    """Note entity - timeline entry for tasks."""

    def __init__(
        self,
        id: UUID,
        task_id: UUID,
        content: str,
        note_type: NoteType = NoteType.COMMENT,
        author_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.task_id = task_id
        self.content = content
        self.note_type = note_type
        self.author_id = author_id
        self.created_at = created_at or datetime.now(UTC)
        self.updated_at = updated_at or datetime.now(UTC)

    @classmethod
    def create(
        cls,
        task_id: UUID,
        content: str,
        author_id: Optional[UUID] = None,
        note_type: NoteType = NoteType.COMMENT,
    ) -> "Note":
        """Create a new note."""
        return cls(
            id=uuid4(),
            task_id=task_id,
            content=content,
            note_type=note_type,
            author_id=author_id,
        )

    @classmethod
    def create_system_note(
        cls,
        task_id: UUID,
        content: str,
    ) -> "Note":
        """Create a system note (author_id = None)."""
        return cls(
            id=uuid4(),
            task_id=task_id,
            content=content,
            note_type=NoteType.SYSTEM,
            author_id=None,
        )
