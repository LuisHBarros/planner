"""Tests for UnitOfWork and CreateTaskUseCase with DTO."""
from datetime import datetime, UTC
from typing import List, Optional
from uuid import UUID, uuid4

import pytest

from app.application.ports.unit_of_work import UnitOfWork
from app.application.use_cases.create_task import CreateTaskUseCase
from app.application.use_cases.dtos import CreateTaskInputDTO
from app.application.ports.event_bus import EventBus
from app.application.events.domain_events import TaskCreated
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import TaskPriority, TaskStatus
from app.domain.models.project import Project
from app.domain.models.role import Role
from app.domain.models.task import Task
from app.domain.models.note import Note
from app.domain.services.ranking import calculate_rank_index


class InMemoryEventBus(EventBus):
    """Simple in-memory EventBus for testing."""

    def __init__(self) -> None:
        self.emitted_events = []

    def emit(self, event) -> None:  # type: ignore[override]
        self.emitted_events.append(event)


class InMemoryProjectRepo:
    def __init__(self) -> None:
        self.projects = {}

    def save(self, project: Project) -> None:
        self.projects[project.id] = project

    def find_by_id(self, project_id: UUID) -> Optional[Project]:
        return self.projects.get(project_id)


class InMemoryRoleRepo:
    def __init__(self) -> None:
        self.roles = {}

    def save(self, role: Role) -> None:
        self.roles[role.id] = role

    def find_by_id(self, role_id: UUID) -> Optional[Role]:
        return self.roles.get(role_id)


class InMemoryTaskRepo:
    def __init__(self) -> None:
        self.tasks = {}

    def save(self, task: Task) -> None:
        self.tasks[task.id] = task

    def find_by_project_id(self, project_id: UUID) -> List[Task]:
        return [t for t in self.tasks.values() if t.project_id == project_id]


class InMemoryNoteRepo:
    def __init__(self) -> None:
        self.notes = {}

    def save(self, note: Note) -> None:
        self.notes[note.id] = note


class FakeUnitOfWork(UnitOfWork):
    """In-memory UnitOfWork used to validate UoW semantics at application level."""

    def __init__(self) -> None:
        self.companies = None  # type: ignore[assignment]
        self.teams = None  # type: ignore[assignment]
        self.users = None  # type: ignore[assignment]
        self.roles = InMemoryRoleRepo()
        self.projects = InMemoryProjectRepo()
        self.tasks = InMemoryTaskRepo()
        self.task_dependencies = None  # type: ignore[assignment]
        self.notes = InMemoryNoteRepo()
        self.team_invites = None  # type: ignore[assignment]
        self.team_members = None  # type: ignore[assignment]

        self.committed = False
        self.rolled_back = False

    def __enter__(self) -> "FakeUnitOfWork":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is None:
            self.commit()
        else:
            self.rollback()

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


def _make_project_and_role(uow: FakeUnitOfWork) -> tuple[Project, Role]:
    project = Project.create(team_id=uuid4(), name="Proj", description="Desc")
    role = Role.create(
        team_id=project.team_id,
        name="Dev",
        level=1,
        base_capacity=40,
        description="Dev role",
    )
    uow.projects.save(project)
    uow.roles.save(role)
    return project, role


class TestCreateTaskUseCaseWithUoW:
    def test_success_commits_unit_of_work_and_emits_event(self):
        """On success, UoW is committed and TaskCreated is emitted."""
        uow = FakeUnitOfWork()
        project, role = _make_project_and_role(uow)
        event_bus = InMemoryEventBus()
        use_case = CreateTaskUseCase(uow=uow, event_bus=event_bus)

        input_dto = CreateTaskInputDTO(
            project_id=project.id,
            title="Task 1",
            description="Test task",
            role_responsible_id=role.id,
            priority=TaskPriority.HIGH,
            due_date=None,
            created_by=uuid4(),
        )

        task = use_case.execute(input_dto)

        # UoW semantics
        assert uow.committed is True
        assert uow.rolled_back is False

        # Task was persisted in repository
        tasks_for_project = uow.tasks.find_by_project_id(project.id)
        assert task in tasks_for_project

        # Rank index uses domain ranking service
        assert task.rank_index == calculate_rank_index(0, [])

        # Event emitted
        assert len(event_bus.emitted_events) == 1
        event = event_bus.emitted_events[0]
        assert isinstance(event, TaskCreated)
        assert event.task_id == task.id

    def test_business_rule_violation_rolls_back_unit_of_work(self):
        """If a business rule fails, UoW is rolled back (no commit)."""
        uow = FakeUnitOfWork()
        project, _role = _make_project_and_role(uow)

        # Role that does not belong to the project team
        other_role = Role.create(
            team_id=uuid4(),
            name="Other",
            level=1,
            base_capacity=40,
            description="Other role",
        )
        uow.roles.save(other_role)

        event_bus = InMemoryEventBus()
        use_case = CreateTaskUseCase(uow=uow, event_bus=event_bus)

        input_dto = CreateTaskInputDTO(
            project_id=project.id,
            title="Task 1",
            description="Test task",
            role_responsible_id=other_role.id,
            priority=TaskPriority.MEDIUM,
            due_date=None,
            created_by=None,
        )

        with pytest.raises(BusinessRuleViolation):
            use_case.execute(input_dto)

        assert uow.committed is False
        assert uow.rolled_back is True
        assert uow.tasks.find_by_project_id(project.id) == []


class DummySession:
    """Minimal SQLAlchemy-like session for testing SqlAlchemyUnitOfWork behavior."""

    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        self.closed = True


def test_sqlalchemy_uow_commits_and_closes_session(monkeypatch):
    """SqlAlchemyUnitOfWork should commit and close session on success."""
    from app.infrastructure.persistence.uow import SqlAlchemyUnitOfWork

    dummy_session = DummySession()
    uow = SqlAlchemyUnitOfWork(session_factory=lambda: dummy_session)  # type: ignore[arg-type]

    # We don't exercise repository wiring here; we just check commit/close behavior
    with uow:
        assert dummy_session.closed is False

    assert dummy_session.committed is True
    assert dummy_session.rolled_back is False
    assert dummy_session.closed is True


def test_sqlalchemy_uow_rolls_back_on_error():
    """SqlAlchemyUnitOfWork should rollback and close session on exception."""
    from app.infrastructure.persistence.uow import SqlAlchemyUnitOfWork

    dummy_session = DummySession()
    uow = SqlAlchemyUnitOfWork(session_factory=lambda: dummy_session)  # type: ignore[arg-type]

    with pytest.raises(RuntimeError):
        with uow:
            raise RuntimeError("boom")

    assert dummy_session.committed is False
    assert dummy_session.rolled_back is True
    assert dummy_session.closed is True

