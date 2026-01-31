"""Tests for CreateProjectUseCase (UC-010)."""
import pytest
from unittest.mock import Mock, MagicMock

from app.application.dtos.project_dtos import CreateProjectInput
from app.application.use_cases.create_project import CreateProjectUseCase
from app.domain.models.user import User
from app.domain.models.value_objects import UserId
from app.domain.exceptions import BusinessRuleViolation


class TestCreateProjectUseCase:
    """Test suite for UC-010: Create Project."""

    def setup_method(self):
        self.uow = MagicMock()
        self.event_bus = Mock()
        self.use_case = CreateProjectUseCase(
            uow=self.uow,
            event_bus=self.event_bus,
        )
        self.user = User.create(email="test@example.com", name="Test User")
        self.uow.users.find_by_id.return_value = self.user

    def test_creates_project_successfully(self):
        """User can create a project."""
        input_dto = CreateProjectInput(
            name="My Project",
            description="Test project",
            created_by=self.user.id,
        )

        result = self.use_case.execute(input_dto)

        assert result.name == "My Project"
        self.uow.projects.save.assert_called_once()
        self.uow.commit.assert_called_once()

    def test_creator_becomes_manager(self):
        """BR-PROJ-001: Creator is automatically Manager."""
        input_dto = CreateProjectInput(
            name="My Project",
            created_by=self.user.id,
        )

        self.use_case.execute(input_dto)

        self.uow.project_members.save.assert_called_once()
        saved_member = self.uow.project_members.save.call_args[0][0]
        assert saved_member.is_manager is True

    def test_emits_project_created_event(self):
        """Event is emitted on creation."""
        input_dto = CreateProjectInput(
            name="My Project",
            created_by=self.user.id,
        )

        self.use_case.execute(input_dto)

        self.event_bus.emit.assert_called_once()

    def test_fails_if_user_not_found(self):
        """Raises error if user doesn't exist."""
        self.uow.users.find_by_id.return_value = None
        input_dto = CreateProjectInput(
            name="My Project",
            created_by=UserId(),
        )

        with pytest.raises(BusinessRuleViolation):
            self.use_case.execute(input_dto)
