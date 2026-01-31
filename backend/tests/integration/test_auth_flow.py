"""Integration test for auth flow."""
from datetime import datetime, timedelta, timezone

from app.application.dtos.auth_dtos import LoginUserInput, RegisterUserInput, VerifyMagicLinkInput
from app.application.use_cases.login_user import LoginUserUseCase
from app.application.use_cases.register_user import RegisterUserUseCase
from app.application.use_cases.verify_magic_link import VerifyMagicLinkUseCase
from app.domain.models.value_objects import InviteToken, UtcDateTime
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


def test_auth_flow_register_login_verify(session_factory):
    """Register, login, and verify magic link."""
    uow = make_uow(session_factory)
    register = RegisterUserUseCase(uow=uow, event_bus=uow.event_bus)
    register.execute(RegisterUserInput(email="test@example.com", name="Test"))

    login = LoginUserUseCase(uow=uow)
    expires_at = UtcDateTime(datetime.now(timezone.utc) + timedelta(hours=1))
    login_output = login.execute(LoginUserInput(email="test@example.com", expires_at=expires_at))

    verify = VerifyMagicLinkUseCase(uow=uow)
    user_output = verify.execute(VerifyMagicLinkInput(token=InviteToken(str(login_output.token))))

    assert user_output.email == "test@example.com"
