"""Task-related DTOs."""
from dataclasses import dataclass
from typing import Optional

from app.domain.models.enums import AbandonmentType, ProgressSource, TaskStatus, WorkloadStatus
from app.domain.models.task import Task
from app.domain.models.task_report import TaskReport
from app.domain.models.value_objects import (
    ProjectId,
    RoleId,
    TaskId,
    TaskReportId,
    UserId,
    UtcDateTime,
)


@dataclass(frozen=True)
class CreateTaskInput:
    """Input for creating a task."""
    project_id: ProjectId
    title: str
    description: Optional[str] = None
    role_id: Optional[RoleId] = None


@dataclass(frozen=True)
class TaskOutput:
    """Task output DTO."""
    id: TaskId
    project_id: ProjectId
    title: str
    description: Optional[str]
    status: TaskStatus
    difficulty: Optional[int]
    role_id: Optional[RoleId]
    assigned_to: Optional[UserId]
    expected_start_date: Optional[UtcDateTime]
    expected_end_date: Optional[UtcDateTime]
    actual_start_date: Optional[UtcDateTime]
    actual_end_date: Optional[UtcDateTime]

    @staticmethod
    def from_domain(task: Task) -> "TaskOutput":
        """Create output DTO from domain model."""
        return TaskOutput(
            id=task.id,
            project_id=task.project_id,
            title=task.title,
            description=task.description,
            status=task.status,
            difficulty=task.difficulty,
            role_id=task.role_id,
            assigned_to=task.assigned_to,
            expected_start_date=task.expected_start_date,
            expected_end_date=task.expected_end_date,
            actual_start_date=task.actual_start_date,
            actual_end_date=task.actual_end_date,
        )


@dataclass(frozen=True)
class SetTaskDifficultyInput:
    """Input for setting task difficulty."""
    task_id: TaskId
    difficulty: int


@dataclass(frozen=True)
class TaskDependencyInput:
    """Input for task dependency operations."""
    task_id: TaskId
    depends_on_id: TaskId


@dataclass(frozen=True)
class SelectTaskInput:
    """Input for selecting a task."""
    task_id: TaskId
    user_id: UserId


@dataclass(frozen=True)
class AbandonTaskInput:
    """Input for abandoning a task."""
    task_id: TaskId
    user_id: UserId
    abandonment_type: AbandonmentType
    note: Optional[str] = None


@dataclass(frozen=True)
class TaskReportInput:
    """Input for creating a task report."""
    task_id: TaskId
    author_id: UserId
    progress: int
    source: ProgressSource
    note: Optional[str] = None


@dataclass(frozen=True)
class CalculateProgressInput:
    """Input for calculating progress via LLM."""
    task_id: TaskId
    author_id: UserId


@dataclass(frozen=True)
class TaskReportOutput:
    """Task report output DTO."""
    id: TaskReportId
    task_id: TaskId
    author_id: UserId
    progress: int
    source: ProgressSource
    note: Optional[str]
    created_at: UtcDateTime

    @staticmethod
    def from_domain(report: TaskReport) -> "TaskReportOutput":
        """Create output DTO from domain model."""
        return TaskReportOutput(
            id=report.id,
            task_id=report.task_id,
            author_id=report.author_id,
            progress=report.progress,
            source=report.source,
            note=report.note,
            created_at=report.created_at,
        )


@dataclass(frozen=True)
class WorkloadOutput:
    """Workload output DTO."""
    workload_score: int
    capacity: float
    status: WorkloadStatus
