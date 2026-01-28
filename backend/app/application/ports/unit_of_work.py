"""Unit of Work port for application layer.

This abstraction coordinates transactional work across multiple repositories
while keeping use cases independent of SQLAlchemy, FastAPI or any other
framework.
"""
from __future__ import annotations

from typing import Protocol, ContextManager

from app.application.ports.company_repository import CompanyRepository
from app.application.ports.team_repository import TeamRepository
from app.application.ports.user_repository import UserRepository
from app.application.ports.role_repository import RoleRepository
from app.application.ports.project_repository import ProjectRepository
from app.application.ports.task_repository import TaskRepository
from app.application.ports.task_dependency_repository import TaskDependencyRepository
from app.application.ports.note_repository import NoteRepository
from app.application.ports.team_invite_repository import TeamInviteRepository
from app.application.ports.team_member_repository import TeamMemberRepository


class UnitOfWork(Protocol, ContextManager["UnitOfWork"]):
    """Coordinates a set of changes as a single atomic unit.

    Usage in a use case:

        with self.uow:
            task = self.uow.tasks.save(...)
            ...
        # commit/rollback is handled by the implementation
    """

    # Repository accessors exposed to the application layer
    companies: CompanyRepository
    teams: TeamRepository
    users: UserRepository
    roles: RoleRepository
    projects: ProjectRepository
    tasks: TaskRepository
    task_dependencies: TaskDependencyRepository
    notes: NoteRepository
    team_invites: TeamInviteRepository
    team_members: TeamMemberRepository

    def __enter__(self) -> "UnitOfWork":  # pragma: no cover - protocol
        ...

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - protocol
        ...

    def commit(self) -> None:
        """Commit the current transaction."""
        ...

    def rollback(self) -> None:
        """Rollback the current transaction."""
        ...

