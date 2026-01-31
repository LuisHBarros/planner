"""Tests for application ports."""
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
from app.application.ports.unit_of_work import UnitOfWork
from app.application.ports.user_repository import UserRepository


def test_ports_are_protocols():
    """All ports are Protocols."""
    ports = [
        EmailService,
        EventBus,
        LlmService,
        MagicLinkRepository,
        NotificationPreferenceRepository,
        ProjectInviteRepository,
        ProjectMemberRepository,
        ProjectRepository,
        RoleRepository,
        ScheduleHistoryRepository,
        TaskAbandonmentRepository,
        TaskAssignmentHistoryRepository,
        TaskDependencyRepository,
        TaskReportRepository,
        TaskRepository,
        UnitOfWork,
        UserRepository,
    ]
    assert all(issubclass(port, Protocol) for port in ports)
