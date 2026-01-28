"""DTOs for application use cases."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.domain.models.enums import TaskPriority


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

