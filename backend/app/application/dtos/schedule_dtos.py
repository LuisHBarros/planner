"""Schedule-related DTOs."""
from dataclasses import dataclass
from typing import Optional

from app.domain.models.project_schedule_history import ProjectScheduleHistory
from app.domain.models.task_schedule_history import TaskScheduleHistory
from app.domain.models.value_objects import (
    ProjectId,
    ProjectScheduleHistoryId,
    TaskId,
    TaskScheduleHistoryId,
    UtcDateTime,
)
from app.domain.models.enums import ScheduleChangeReason


@dataclass(frozen=True)
class DetectDelayInput:
    """Input for delay detection."""
    task_id: TaskId


@dataclass(frozen=True)
class PropagateScheduleInput:
    """Input for schedule propagation."""
    task_id: TaskId
    delay_delta_seconds: int


@dataclass(frozen=True)
class UpdateProjectDateInput:
    """Input for updating project date."""
    project_id: ProjectId
    new_end_date: UtcDateTime
    reason: ScheduleChangeReason


@dataclass(frozen=True)
class ManualDateOverrideInput:
    """Input for manual task date override."""
    task_id: TaskId
    new_start_date: UtcDateTime
    new_end_date: UtcDateTime


@dataclass(frozen=True)
class TaskScheduleHistoryOutput:
    """Task schedule history output DTO."""
    id: TaskScheduleHistoryId
    task_id: TaskId
    previous_start: UtcDateTime
    previous_end: UtcDateTime
    new_start: UtcDateTime
    new_end: UtcDateTime
    reason: ScheduleChangeReason

    @staticmethod
    def from_domain(history: TaskScheduleHistory) -> "TaskScheduleHistoryOutput":
        """Create output DTO from domain model."""
        return TaskScheduleHistoryOutput(
            id=history.id,
            task_id=history.task_id,
            previous_start=history.previous_start,
            previous_end=history.previous_end,
            new_start=history.new_start,
            new_end=history.new_end,
            reason=history.reason,
        )


@dataclass(frozen=True)
class ProjectScheduleHistoryOutput:
    """Project schedule history output DTO."""
    id: ProjectScheduleHistoryId
    project_id: ProjectId
    previous_end: UtcDateTime
    new_end: UtcDateTime
    reason: ScheduleChangeReason

    @staticmethod
    def from_domain(history: ProjectScheduleHistory) -> "ProjectScheduleHistoryOutput":
        """Create output DTO from domain model."""
        return ProjectScheduleHistoryOutput(
            id=history.id,
            project_id=history.project_id,
            previous_end=history.previous_end,
            new_end=history.new_end,
            reason=history.reason,
        )
