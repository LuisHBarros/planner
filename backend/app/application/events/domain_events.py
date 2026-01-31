"""Domain events."""
from dataclasses import dataclass

from app.domain.models.enums import AbandonmentType
from app.domain.models.value_objects import ProjectId, TaskId, UserId, ProjectInviteId


@dataclass(frozen=True)
class UserRegistered:
    """Emitted when a user registers."""
    user_id: UserId
    email: str


@dataclass(frozen=True)
class ProjectCreated:
    """Emitted when a project is created."""
    project_id: ProjectId
    created_by: UserId
    name: str


@dataclass(frozen=True)
class ProjectInviteCreated:
    """Emitted when an invite is created."""
    invite_id: ProjectInviteId
    project_id: ProjectId
    email: str


@dataclass(frozen=True)
class ProjectInviteAccepted:
    """Emitted when an invite is accepted."""
    invite_id: ProjectInviteId
    project_id: ProjectId
    user_id: UserId


@dataclass(frozen=True)
class TaskCreated:
    """Emitted when a task is created."""
    task_id: TaskId
    project_id: ProjectId


@dataclass(frozen=True)
class TaskAssigned:
    """Emitted when a task is assigned."""
    task_id: TaskId
    user_id: UserId


@dataclass(frozen=True)
class TaskAbandoned:
    """Emitted when a task is abandoned."""
    task_id: TaskId
    user_id: UserId
    abandonment_type: AbandonmentType


@dataclass(frozen=True)
class TaskCompleted:
    """Emitted when a task is completed."""
    task_id: TaskId


@dataclass(frozen=True)
class NotificationRequested:
    """Emitted when a notification should be sent."""
    notification_type: str
    project_id: ProjectId | None = None
    task_id: TaskId | None = None
    user_id: UserId | None = None
