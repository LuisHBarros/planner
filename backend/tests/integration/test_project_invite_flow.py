"""Integration test for project invite flow."""
from app.application.dtos.project_dtos import AcceptInviteInput, CreateProjectInput, CreateProjectInviteInput
from app.application.use_cases.accept_invite import AcceptInviteUseCase
from app.application.use_cases.create_project import CreateProjectUseCase
from app.application.use_cases.create_project_invite import CreateProjectInviteUseCase
from app.domain.models.enums import MemberLevel
from app.domain.models.user import User
from app.domain.models.value_objects import InviteToken, UserId
from app.infrastructure.email.email_service import MockEmailService
from app.infrastructure.events.in_memory_event_bus import InMemoryEventBus
from app.infrastructure.llm.llm_service import SimpleLlmService
from app.infrastructure.persistence.uow import SqlAlchemyUnitOfWork


def make_uow(session_factory):
    """Create unit of work for integration tests."""
    return SqlAlchemyUnitOfWork(
        session_factory=session_factory,
        event_bus=InMemoryEventBus(),
        email_service=MockEmailService(),
        llm_service=SimpleLlmService(api_url=None, api_key=None),
    )


def test_invite_flow(session_factory):
    """Create project invite and accept it."""
    uow = make_uow(session_factory)
    manager_id = UserId()
    with uow:
        uow.users.save(User(id=manager_id, email="manager@example.com", name="Manager"))
        uow.commit()

    create_project = CreateProjectUseCase(uow=uow, event_bus=uow.event_bus)
    project_output = create_project.execute(CreateProjectInput(
        name="Proj",
        created_by=manager_id,
    ))

    invite_uc = CreateProjectInviteUseCase(uow=uow, event_bus=uow.event_bus)
    invite_output = invite_uc.execute(CreateProjectInviteInput(
        project_id=project_output.id,
        email="member@example.com",
    ))

    accept_uc = AcceptInviteUseCase(uow=uow, event_bus=uow.event_bus)
    accept_output = accept_uc.execute(AcceptInviteInput(
        token=InviteToken(str(invite_output.token)),
        user_id=UserId(),
        level=MemberLevel.MID,
        base_capacity=10,
    ))

    assert accept_output.status.value == "accepted"
