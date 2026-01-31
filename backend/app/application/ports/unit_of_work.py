"""Unit of Work port."""
from typing import Protocol

from app.application.ports.email_service import EmailService
from app.application.ports.event_bus import EventBus
from app.application.ports.llm_service import LlmService
from app.application.ports.magic_link_repository import MagicLinkRepository
from app.application.ports.notification_preference_repository import NotificationPreferenceRepository
from app.application.ports.project_invite_repository import ProjectInviteRepository
from app.application.ports.project_member_repository import ProjectMemberRepository
from app.application.ports.project_repository import ProjectRepository
from app.application.ports.role_repository import RoleRepository
from app.application.ports.schedule_history_repository import ScheduleHistoryRepository
from app.application.ports.task_abandonment_repository import TaskAbandonmentRepository
from app.application.ports.task_assignment_history_repository import TaskAssignmentHistoryRepository
from app.application.ports.task_dependency_repository import TaskDependencyRepository
from app.application.ports.task_report_repository import TaskReportRepository
from app.application.ports.task_repository import TaskRepository
from app.application.ports.user_repository import UserRepository


class UnitOfWork(Protocol):
    """Unit of Work interface coordinating repositories."""

    users: UserRepository
    projects: ProjectRepository
    project_members: ProjectMemberRepository
    roles: RoleRepository
    project_invites: ProjectInviteRepository
    tasks: TaskRepository
    task_dependencies: TaskDependencyRepository
    task_reports: TaskReportRepository
    task_abandonments: TaskAbandonmentRepository
    task_assignment_history: TaskAssignmentHistoryRepository
    schedule_history: ScheduleHistoryRepository
    notification_preferences: NotificationPreferenceRepository
    magic_links: MagicLinkRepository

    event_bus: EventBus
    email_service: EmailService
    llm_service: LlmService

    def __enter__(self) -> "UnitOfWork":
        """Begin a unit of work."""
        ...

    def __exit__(self, exc_type, exc, tb) -> None:
        """Exit a unit of work."""
        ...

    def commit(self) -> None:
        """Commit the unit of work."""
        ...
