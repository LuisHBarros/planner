"""Tests for RegisterUserUseCase (UC-001)."""
import pytest
from unittest.mock import Mock, MagicMock

from app.application.dtos.auth_dtos import RegisterUserInput
from app.application.use_cases.register_user import RegisterUserUseCase
from app.domain.exceptions import BusinessRuleViolation


class TestRegisterUserUseCase:
    """Test suite for UC-001: Register User."""

    def setup_method(self):
        self.uow = MagicMock()
        self.event_bus = Mock()
        self.use_case = RegisterUserUseCase(uow=self.uow, event_bus=self.event_bus)

    def test_registers_user_successfully(self):
        """Registers a new user."""
        self.uow.users.find_by_email.return_value = None
        input_dto = RegisterUserInput(email="test@example.com", name="Test User")

        result = self.use_case.execute(input_dto)

        assert result.email == "test@example.com"
        self.uow.users.save.assert_called_once()
        self.uow.commit.assert_called_once()
        self.event_bus.emit.assert_called_once()

    def test_fails_if_email_exists(self):
        """Fails if email already registered."""
        self.uow.users.find_by_email.return_value = object()
        input_dto = RegisterUserInput(email="test@example.com", name="Test User")

        with pytest.raises(BusinessRuleViolation):
            self.use_case.execute(input_dto)
