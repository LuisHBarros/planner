"""Tests for auth use cases."""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from app.application.dtos.auth_dtos import LoginUserInput, VerifyMagicLinkInput
from app.application.use_cases.login_user import LoginUserUseCase
from app.application.use_cases.verify_magic_link import VerifyMagicLinkUseCase
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.magic_link import MagicLink
from app.domain.models.user import User
from app.domain.models.value_objects import InviteToken, UserId, UtcDateTime


def test_login_user_creates_magic_link_and_sends_email():
    """Login creates magic link and sends email."""
    uow = MagicMock()
    user = User.create(email="test@example.com", name="Test")
    uow.users.find_by_email.return_value = user
    use_case = LoginUserUseCase(uow)
    expires_at = UtcDateTime(datetime.now(timezone.utc) + timedelta(hours=1))

    result = use_case.execute(LoginUserInput(email="test@example.com", expires_at=expires_at))

    assert result.expires_at == expires_at
    uow.magic_links.save.assert_called_once()
    uow.email_service.send_magic_link.assert_called_once()
    uow.commit.assert_called_once()


def test_login_user_fails_if_user_missing():
    """Login fails when user does not exist."""
    uow = MagicMock()
    uow.users.find_by_email.return_value = None
    use_case = LoginUserUseCase(uow)
    expires_at = UtcDateTime(datetime.now(timezone.utc) + timedelta(hours=1))

    with pytest.raises(BusinessRuleViolation):
        use_case.execute(LoginUserInput(email="missing@example.com", expires_at=expires_at))


def test_verify_magic_link_consumes_and_returns_user():
    """Verify magic link consumes link and returns user."""
    uow = MagicMock()
    user = User.create(email="test@example.com", name="Test")
    token = InviteToken("token")
    expires_at = UtcDateTime(datetime.now(timezone.utc) + timedelta(hours=1))
    link = MagicLink.create(token=token, user_id=user.id, expires_at=expires_at)
    uow.magic_links.find_by_token.return_value = link
    uow.users.find_by_id.return_value = user
    use_case = VerifyMagicLinkUseCase(uow)

    result = use_case.execute(VerifyMagicLinkInput(token=token))

    assert result.id == user.id
    uow.magic_links.save.assert_called_once()
    uow.commit.assert_called_once()


def test_verify_magic_link_fails_if_missing():
    """Verify fails if link not found."""
    uow = MagicMock()
    uow.magic_links.find_by_token.return_value = None
    use_case = VerifyMagicLinkUseCase(uow)

    with pytest.raises(BusinessRuleViolation):
        use_case.execute(VerifyMagicLinkInput(token=InviteToken("missing")))
