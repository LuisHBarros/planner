"""Unit of Work implementation."""
from __future__ import annotations

from sqlalchemy.orm import Session, sessionmaker

from app.application.ports.email_service import EmailService
from app.application.ports.event_bus import EventBus
from app.application.ports.llm_service import LlmService
from app.application.ports.unit_of_work import UnitOfWork
from app.infrastructure.persistence.repositories import (
    SqlAlchemyMagicLinkRepository,
    SqlAlchemyNotificationPreferenceRepository,
    SqlAlchemyProjectInviteRepository,
    SqlAlchemyProjectMemberRepository,
    SqlAlchemyProjectRepository,
    SqlAlchemyRoleRepository,
    SqlAlchemyScheduleHistoryRepository,
    SqlAlchemyTaskAbandonmentRepository,
    SqlAlchemyTaskAssignmentHistoryRepository,
    SqlAlchemyTaskDependencyRepository,
    SqlAlchemyTaskReportRepository,
    SqlAlchemyTaskRepository,
    SqlAlchemyUserRepository,
)


class SqlAlchemyUnitOfWork(UnitOfWork):
    """SQLAlchemy-backed Unit of Work."""

    def __init__(
        self,
        session_factory: sessionmaker[Session],
        event_bus: EventBus,
        email_service: EmailService,
        llm_service: LlmService,
    ):
        self.session_factory = session_factory
        self.event_bus = event_bus
        self.email_service = email_service
        self.llm_service = llm_service
        self.session: Session | None = None

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self.session = self.session_factory()
        self.users = SqlAlchemyUserRepository(self.session)
        self.projects = SqlAlchemyProjectRepository(self.session)
        self.project_members = SqlAlchemyProjectMemberRepository(self.session)
        self.roles = SqlAlchemyRoleRepository(self.session)
        self.project_invites = SqlAlchemyProjectInviteRepository(self.session)
        self.tasks = SqlAlchemyTaskRepository(self.session)
        self.task_dependencies = SqlAlchemyTaskDependencyRepository(self.session)
        self.task_reports = SqlAlchemyTaskReportRepository(self.session)
        self.task_abandonments = SqlAlchemyTaskAbandonmentRepository(self.session)
        self.task_assignment_history = SqlAlchemyTaskAssignmentHistoryRepository(self.session)
        self.schedule_history = SqlAlchemyScheduleHistoryRepository(self.session)
        self.notification_preferences = SqlAlchemyNotificationPreferenceRepository(self.session)
        self.magic_links = SqlAlchemyMagicLinkRepository(self.session)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.session is None:
            return
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()

    def commit(self) -> None:
        if self.session is None:
            return
        self.session.commit()
