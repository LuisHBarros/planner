"""Tests for CreateProjectInviteUseCase (UC-020)."""
import pytest
from unittest.mock import Mock, MagicMock

from app.application.dtos.project_dtos import CreateProjectInviteInput
from app.application.use_cases.create_project_invite import CreateProjectInviteUseCase
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.project import Project
from app.domain.models.value_objects import ProjectId, UserId


class TestCreateProjectInviteUseCase:
    """Test suite for UC-020: Create Project Invite."""

    def setup_method(self):
        self.uow = MagicMock()
        self.event_bus = Mock()
        self.use_case = CreateProjectInviteUseCase(self.uow, self.event_bus)
        self.project = Project.create(name="Proj", created_by=UserId())
        self.uow.projects.find_by_id.return_value = self.project

    def test_creates_invite(self):
        """Creates invite and commits."""
        input_dto = CreateProjectInviteInput(
            project_id=self.project.id,
            email="invitee@example.com",
        )

        result = self.use_case.execute(input_dto)

        assert result.email == "invitee@example.com"
        self.uow.project_invites.save.assert_called_once()
        self.uow.commit.assert_called_once()
        self.event_bus.emit.assert_called_once()

    def test_fails_if_project_missing(self):
        """Fails if project not found."""
        self.uow.projects.find_by_id.return_value = None
        input_dto = CreateProjectInviteInput(
            project_id=ProjectId(),
            email="invitee@example.com",
        )

        with pytest.raises(BusinessRuleViolation):
            self.use_case.execute(input_dto)
