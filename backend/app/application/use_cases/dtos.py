"""DTOs for application use cases."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from app.domain.models.enums import TaskPriority, ScheduleChangeReason


@dataclass(frozen=True)
class CreateTaskInputDTO:
    """Input data required to create a task (UC-005).

    This object is framework-agnostic and used by the application layer
    instead of Pydantic models or ORM entities.
    """

    project_id: UUID
    title: str
    description: str
    role_responsible_id: UUID
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    created_by: Optional[UUID] = None


@dataclass(frozen=True)
class DelayChainEntryDTO:
    """A single entry in a delay chain (UC-030).

    Represents one schedule change event in the causal chain.
    """

    task_id: UUID
    task_title: str
    old_expected_start: Optional[datetime]
    old_expected_end: Optional[datetime]
    new_expected_start: Optional[datetime]
    new_expected_end: Optional[datetime]
    reason: ScheduleChangeReason
    caused_by_task_id: Optional[UUID]
    caused_by_task_title: Optional[str]
    changed_by_user_id: Optional[UUID]
    created_at: datetime


@dataclass(frozen=True)
class DelayChainOutputDTO:
    """Output for delay chain retrieval (UC-030).

    Contains the complete causal chain of delays for a task,
    enabling root cause analysis.
    """

    task_id: UUID
    task_title: str
    is_delayed: bool
    total_delay_days: Optional[float]
    entries: List[DelayChainEntryDTO] = field(default_factory=list)
    root_cause_task_id: Optional[UUID] = None
    root_cause_task_title: Optional[str] = None

