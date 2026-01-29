"""SQLAlchemy implementation of the UnitOfWork port."""
from __future__ import annotations

from typing import Callable

from sqlalchemy.orm import Session

from app.application.ports.unit_of_work import UnitOfWork
from app.infrastructure.database import SessionLocal
from app.infrastructure.persistence.repositories import (
    SqlAlchemyCompanyRepository,
    SqlAlchemyTeamRepository,
    SqlAlchemyUserRepository,
    SqlAlchemyRoleRepository,
    SqlAlchemyProjectRepository,
    SqlAlchemyTaskRepository,
    SqlAlchemyTaskDependencyRepository,
    SqlAlchemyNoteRepository,
    SqlAlchemyTeamInviteRepository,
    SqlAlchemyTeamMemberRepository,
    SqlAlchemyScheduleHistoryRepository,
)


class SqlAlchemyUnitOfWork(UnitOfWork):
    """Unit of Work backed by a SQLAlchemy session.

    A new session is created for each `with` block and disposed afterwards.
    """

    def __init__(self, session_factory: Callable[[], Session] | None = None) -> None:
        self._session_factory: Callable[[], Session] = session_factory or SessionLocal
        self._session: Session | None = None

        # Repository attributes (initialized in __enter__)
        self.companies = None  # type: ignore[assignment]
        self.teams = None  # type: ignore[assignment]
        self.users = None  # type: ignore[assignment]
        self.roles = None  # type: ignore[assignment]
        self.projects = None  # type: ignore[assignment]
        self.tasks = None  # type: ignore[assignment]
        self.task_dependencies = None  # type: ignore[assignment]
        self.notes = None  # type: ignore[assignment]
        self.team_invites = None  # type: ignore[assignment]
        self.team_members = None  # type: ignore[assignment]
        self.schedule_history = None  # type: ignore[assignment]

    @property
    def session(self) -> Session:
        if self._session is None:  # pragma: no cover - defensive
            raise RuntimeError("UnitOfWork session accessed outside of context")
        return self._session

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self._session = self._session_factory()

        # Wire repositories for this UoW instance
        self.companies = SqlAlchemyCompanyRepository(self.session)
        self.teams = SqlAlchemyTeamRepository(self.session)
        self.users = SqlAlchemyUserRepository(self.session)
        self.roles = SqlAlchemyRoleRepository(self.session)
        self.projects = SqlAlchemyProjectRepository(self.session)
        self.tasks = SqlAlchemyTaskRepository(self.session)
        self.task_dependencies = SqlAlchemyTaskDependencyRepository(self.session)
        self.notes = SqlAlchemyNoteRepository(self.session)
        self.team_invites = SqlAlchemyTeamInviteRepository(self.session)
        self.team_members = SqlAlchemyTeamMemberRepository(self.session)
        self.schedule_history = SqlAlchemyScheduleHistoryRepository(self.session)

        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            if exc_type is None:
                self.commit()
            else:
                self.rollback()
        finally:
            if self._session is not None:
                self._session.close()
            self._session = None

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

