"""Domain events for event-driven architecture."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.domain.models.enums import TaskStatus, CompletionSource


@dataclass
class DomainEvent:
    """Base class for domain events."""

    timestamp: datetime


@dataclass
class TaskCreated(DomainEvent):
    """Event emitted when a task is created."""

    task_id: UUID
    project_id: UUID
    role_id: UUID
    title: str
    created_by: UUID


@dataclass
class TaskAssigned(DomainEvent):
    """Event emitted when a task is assigned/claimed."""

    task_id: UUID
    user_id: UUID


@dataclass
class TaskStatusChanged(DomainEvent):
    """Event emitted when task status changes."""

    task_id: UUID
    old_status: TaskStatus
    new_status: TaskStatus
    user_id: Optional[UUID] = None


@dataclass
class TaskCompleted(DomainEvent):
    """Event emitted when a task is completed."""

    task_id: UUID
    completed_by: UUID
    lead_time_days: float
    user_id: Optional[UUID] = None


@dataclass
class TaskBlocked(DomainEvent):
    """Event emitted when a task is blocked."""

    task_id: UUID
    reason: str


@dataclass
class TaskUnblocked(DomainEvent):
    """Event emitted when a task is unblocked."""

    task_id: UUID
    user_id: Optional[UUID] = None


@dataclass
class TaskProgressUpdated(DomainEvent):
    """Event emitted when task progress is updated."""

    task_id: UUID
    completion_percentage: int
    source: CompletionSource
    reasoning: Optional[str] = None
    user_id: Optional[UUID] = None


@dataclass
class TasksReranked(DomainEvent):
    """Event emitted when tasks are reranked."""

    project_id: UUID
    task_ids: list[UUID]


@dataclass
class NoteAdded(DomainEvent):
    """Event emitted when a note is added."""

    task_id: UUID
    note_id: UUID
    author_id: Optional[UUID]
    user_id: Optional[UUID] = None