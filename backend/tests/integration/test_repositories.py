"""Integration tests for repositories and UoW."""
from app.domain.models.project import Project
from app.domain.models.task import Task
from app.domain.models.user import User
from app.domain.models.value_objects import InviteToken, UtcDateTime
from app.infrastructure.email.email_service import MockEmailService
from app.infrastructure.events.in_memory_event_bus import InMemoryEventBus
from app.infrastructure.llm.llm_service import SimpleLlmService
from app.infrastructure.persistence.uow import SqlAlchemyUnitOfWork


def make_uow(session_factory):
    """Create a unit of work for tests."""
    return SqlAlchemyUnitOfWork(
        session_factory=session_factory,
        event_bus=InMemoryEventBus(),
        email_service=MockEmailService(),
        llm_service=SimpleLlmService(api_url=None, api_key=None),
    )


def test_user_repository_save_and_find(session_factory):
    """Saves and retrieves a user."""
    uow = make_uow(session_factory)
    user = User.create(email="test@example.com", name="Test")

    with uow:
        uow.users.save(user)
        uow.commit()

    with uow:
        loaded = uow.users.find_by_id(user.id)

    assert loaded is not None
    assert loaded.email == "test@example.com"


def test_project_repository_save_and_find(session_factory):
    """Saves and retrieves a project."""
    uow = make_uow(session_factory)
    owner = User.create(email="owner@example.com", name="Owner")
    project = Project.create(name="Proj", created_by=owner.id)

    with uow:
        uow.users.save(owner)
        uow.projects.save(project)
        uow.commit()

    with uow:
        loaded = uow.projects.find_by_id(project.id)

    assert loaded is not None
    assert loaded.name == "Proj"


def test_task_repository_save_and_find(session_factory):
    """Saves and retrieves a task."""
    uow = make_uow(session_factory)
    owner = User.create(email="owner@example.com", name="Owner")
    project = Project.create(name="Proj", created_by=owner.id)
    task = Task.create(project_id=project.id, title="Task")

    with uow:
        uow.users.save(owner)
        uow.projects.save(project)
        uow.tasks.save(task)
        uow.commit()

    with uow:
        loaded = uow.tasks.find_by_id(task.id)

    assert loaded is not None
    assert loaded.title == "Task"


def test_magic_link_repository_save_and_find(session_factory):
    """Saves and retrieves a magic link."""
    uow = make_uow(session_factory)
    user = User.create(email="test@example.com", name="Test")
    token = InviteToken("token")
    from app.domain.models.magic_link import MagicLink

    link = MagicLink.create(token=token, user_id=user.id, expires_at=UtcDateTime())

    with uow:
        uow.users.save(user)
        uow.magic_links.save(link)
        uow.commit()

    with uow:
        loaded = uow.magic_links.find_by_token(token)

    assert loaded is not None
    assert loaded.token.value == "token"
