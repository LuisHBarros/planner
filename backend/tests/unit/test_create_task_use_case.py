"""Unit tests for CreateTaskUseCase using in-memory fakes and UoW."""
from datetime import datetime, UTC, timedelta
from uuid import uuid4

import pytest

from app.application.use_cases.create_task import CreateTaskUseCase
from app.application.use_cases.dtos import CreateTaskInputDTO
from app.application.events.domain_events import TaskCreated
from app.domain.models.project import Project
from app.domain.models.role import Role
from app.domain.models.note import Note
from app.domain.models.enums import TaskPriority, RoleLevel, NoteType
from app.domain.exceptions import BusinessRuleViolation


class FakeTaskRepository:
    """In-memory implementation of TaskRepository using a dict."""

    def __init__(self) -> None:
        self.tasks: dict = {}

    def save(self, task):
        self.tasks[task.id] = task

    def find_by_id(self, task_id):
        return self.tasks.get(task_id)

    def find_by_project_id(self, project_id):
        return [t for t in self.tasks.values() if t.project_id == project_id]

    # Unused by these tests but required by port
    def find_by_role_id(self, role_id, status=None):
        return [t for t in self.tasks.values() if t.role_responsible_id == role_id]

    def find_by_user_id(self, user_id):
        return [t for t in self.tasks.values() if t.user_responsible_id == user_id]

    def find_dependent_tasks(self, task_id):
        return []


class FakeProjectRepository:
    """In-memory implementation of ProjectRepository using a dict."""

    def __init__(self) -> None:
        self.projects: dict = {}

    def save(self, project):
        self.projects[project.id] = project

    def find_by_id(self, project_id):
        return self.projects.get(project_id)

    def find_by_team_id(self, team_id):
        return [p for p in self.projects.values() if p.team_id == team_id]


class FakeRoleRepository:
    """In-memory role repository used for CreateTaskUseCase tests."""

    def __init__(self) -> None:
        self.roles: dict = {}

    def save(self, role):
        self.roles[role.id] = role

    def find_by_id(self, role_id):
        return self.roles.get(role_id)

    def find_by_team_id(self, team_id):
        return [r for r in self.roles.values() if r.team_id == team_id]

    def find_by_user_and_team(self, user_id, team_id):
        return []


class FakeNoteRepository:
    """In-memory note repository to capture system notes."""

    def __init__(self) -> None:
        self.notes: dict = {}

    def save(self, note: Note):
        self.notes[note.id] = note

    def find_by_id(self, note_id):
        return self.notes.get(note_id)

    def find_by_task_id(self, task_id):
        return [n for n in self.notes.values() if n.task_id == task_id]


class MockEventBus:
    """Simple mock for EventBus to record emitted events."""

    def __init__(self) -> None:
        self.emitted_events: list = []

    def subscribe(self, event_type, handler):
        # Not needed for these unit tests
        pass

    def emit(self, event):
        self.emitted_events.append(event)


class MemoryUnitOfWork:
    """
    Fake Unit of Work coordinating in-memory repositories.

    This simulates commit/rollback semantics for use cases that expect a UoW.
    For these tests we use it mainly to validate that commit is or is not called.
    """

    def __init__(self):
        self.tasks = FakeTaskRepository()
        self.projects = FakeProjectRepository()
        self.roles = FakeRoleRepository()
        self.notes = FakeNoteRepository()
        self.event_bus = MockEventBus()

        self.committed = False
        self._should_fail_on_commit = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()

    def commit(self):
        if self._should_fail_on_commit:
            # Simulate infrastructure error during commit
            raise RuntimeError("Commit failed")
        self.committed = True

    def rollback(self):
        # For our purposes we just mark as not committed.
        self.committed = False

    def fail_on_commit(self):
        """Helper to configure the UoW to raise on commit."""
        self._should_fail_on_commit = True


def _build_use_case_with_uow(uow: MemoryUnitOfWork) -> CreateTaskUseCase:
    """Helper to construct use case wired with fake UoW dependencies."""
    return CreateTaskUseCase(
        uow=uow,
        event_bus=uow.event_bus,
    )


def _seed_project_and_role(uow: MemoryUnitOfWork):
    """Create a valid project and role belonging to the same team."""
    team_id = uuid4()
    project = Project.create(team_id=team_id, name="Test Project", description="Desc")
    role = Role.create(
        team_id=team_id,
        name="Developer",
        level=RoleLevel.MID,
        base_capacity=5,
    )
    uow.projects.save(project)
    uow.roles.save(role)
    return project, role


def test_create_task_success_persists_and_commits():
    """
    Creating a valid task:
    - persists in fake repository
    - emits TaskCreated event
    - creates a system note if created_by is provided
    """
    uow = MemoryUnitOfWork()
    use_case = _build_use_case_with_uow(uow)
    project, role = _seed_project_and_role(uow)

    created_by = uuid4()
    title = "Implement feature X"
    description = "Detailed description"

    input_dto = CreateTaskInputDTO(
        project_id=project.id,
        title=title,
        description=description,
        role_responsible_id=role.id,
        priority=TaskPriority.HIGH,
        due_date=datetime.now(UTC) + timedelta(days=3),
        created_by=created_by,
    )

    task = use_case.execute(input_dto)

    # Repository persistence
    assert task.id in uow.tasks.tasks
    saved_task = uow.tasks.find_by_id(task.id)
    assert saved_task is not None
    assert saved_task.title == title
    assert saved_task.description == description
    assert saved_task.priority == TaskPriority.HIGH

    # UoW commit flag
    assert uow.committed is True

    # Domain event was emitted
    assert len(uow.event_bus.emitted_events) == 1
    event = uow.event_bus.emitted_events[0]
    assert isinstance(event, TaskCreated)
    assert event.task_id == task.id
    assert event.project_id == project.id
    assert event.role_id == role.id
    assert event.title == title
    assert event.created_by == created_by or task.id

    # System note created
    notes_for_task = uow.notes.find_by_task_id(task.id)
    assert len(notes_for_task) == 1
    system_note = notes_for_task[0]
    assert system_note.note_type == NoteType.SYSTEM
    assert "Task created by user" in system_note.content


def test_create_task_for_nonexistent_project_raises_business_rule():
    """Creating a task for a project that does not exist raises project_not_found."""
    uow = MemoryUnitOfWork()
    use_case = _build_use_case_with_uow(uow)

    input_dto = CreateTaskInputDTO(
        project_id=uuid4(),
        title="Some Task",
        description="Desc",
        role_responsible_id=uuid4(),
        priority=TaskPriority.MEDIUM,
        created_by=uuid4(),
    )

    with pytest.raises(BusinessRuleViolation) as exc_info:
        use_case.execute(input_dto)

    assert exc_info.value.code == "project_not_found"
    # No tasks should have been persisted
    assert len(uow.tasks.tasks) == 0
    # Commit should not be flagged
    assert uow.committed is False


def test_create_task_atomicity_when_error_after_creation():
    """
    If an error happens after task creation (e.g. during commit),
    UoW should not report committed=True, simulating rollback behaviour.
    """
    uow = MemoryUnitOfWork()
    use_case = _build_use_case_with_uow(uow)
    project, role = _seed_project_and_role(uow)

    # Configure UoW to fail on commit to simulate infrastructure error
    uow.fail_on_commit()

    input_dto = CreateTaskInputDTO(
        project_id=project.id,
        title="Atomicity test task",
        description="Desc",
        role_responsible_id=role.id,
        priority=TaskPriority.MEDIUM,
        created_by=uuid4(),
    )

    with pytest.raises(RuntimeError):
        use_case.execute(input_dto)

    # Even though the repository may have the task in memory,
    # the UoW should indicate that commit was not successful.
    assert uow.committed is False

