"""Domain events for event-driven architecture."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.domain.models.enums import TaskStatus, CompletionSource, AbandonmentType, WorkloadStatus


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


@dataclass
class TaskDelayed(DomainEvent):
    """Event emitted when a task is detected as delayed."""

    task_id: UUID
    delay_seconds: int


@dataclass
class ScheduleChanged(DomainEvent):
    """Event emitted when a task's expected schedule changes (propagation)."""

    task_id: UUID
    old_expected_start: Optional[datetime]
    old_expected_end: Optional[datetime]
    new_expected_start: Optional[datetime]
    new_expected_end: Optional[datetime]
    caused_by_task_id: Optional[UUID]


@dataclass
class ScheduleOverridden(DomainEvent):
    """Event emitted when a manager manually overrides a task schedule."""

    task_id: UUID
    old_expected_start: Optional[datetime]
    old_expected_end: Optional[datetime]
    new_expected_start: Optional[datetime]
    new_expected_end: Optional[datetime]
    changed_by_user_id: Optional[UUID]


# v3.0 Domain Events


@dataclass
class TaskAbandoned(DomainEvent):
    """Event emitted when a task is abandoned (v3.0)."""

    task_id: UUID
    user_id: UUID
    abandonment_type: AbandonmentType
    initiated_by_user_id: UUID


@dataclass
class TaskCancelled(DomainEvent):
    """Event emitted when a task is cancelled (v3.0)."""

    task_id: UUID
    cancelled_by_user_id: UUID
    reason: Optional[str] = None


@dataclass
class WorkloadWarning(DomainEvent):
    """Event emitted when a user's workload reaches warning levels (v3.0)."""

    user_id: UUID
    project_id: UUID
    status: WorkloadStatus
    score: int
    capacity: float


@dataclass
class DifficultySet(DomainEvent):
    """Event emitted when a task's difficulty is set (v3.0)."""

    task_id: UUID
    difficulty: int
    set_by_user_id: UUID