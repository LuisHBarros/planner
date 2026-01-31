"""Tests for project-related use cases."""
import pytest
from unittest.mock import MagicMock

from app.application.dtos.project_dtos import CreateRoleInput, ConfigureProjectLlmInput
from app.application.use_cases.configure_project_llm import ConfigureProjectLlmUseCase
from app.application.use_cases.create_role import CreateRoleUseCase
from app.application.use_cases.get_project import GetProjectUseCase
from app.application.use_cases.view_invite import ViewInviteUseCase
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.project import Project
from app.domain.models.project_invite import ProjectInvite
from app.domain.models.value_objects import InviteToken, ProjectId, UserId


def test_configure_project_llm_updates_project():
    """Configures LLM settings."""
    uow = MagicMock()
    project = Project.create(name="Proj", created_by=UserId())
    uow.projects.find_by_id.return_value = project
    use_case = ConfigureProjectLlmUseCase(uow)

    use_case.execute(ConfigureProjectLlmInput(
        project_id=project.id,
        provider="openai",
        api_key_encrypted="secret",
    ))

    assert project.llm_enabled is True
    uow.projects.save.assert_called_once()
    uow.commit.assert_called_once()


def test_create_role_saves_role():
    """Creates role for project."""
    uow = MagicMock()
    project = Project.create(name="Proj", created_by=UserId())
    uow.projects.find_by_id.return_value = project
    use_case = CreateRoleUseCase(uow)

    result = use_case.execute(CreateRoleInput(
        project_id=project.id,
        name="Engineer",
        description="Dev",
    ))

    assert result.name == "Engineer"
    uow.roles.save.assert_called_once()
    uow.commit.assert_called_once()


def test_get_project_returns_project():
    """Returns project output."""
    uow = MagicMock()
    project = Project.create(name="Proj", created_by=UserId())
    uow.projects.find_by_id.return_value = project
    use_case = GetProjectUseCase(uow)

    result = use_case.execute(project.id)

    assert result.id == project.id


def test_view_invite_returns_invite():
    """Returns invite output by token."""
    uow = MagicMock()
    invite = ProjectInvite.create(
        project_id=ProjectId(),
        email="test@example.com",
        token=InviteToken("token"),
    )
    uow.project_invites.find_by_token.return_value = invite
    use_case = ViewInviteUseCase(uow)

    result = use_case.execute(InviteToken("token"))

    assert result.email == "test@example.com"


def test_view_invite_fails_if_missing():
    """Fails if invite missing."""
    uow = MagicMock()
    uow.project_invites.find_by_token.return_value = None
    use_case = ViewInviteUseCase(uow)

    with pytest.raises(BusinessRuleViolation):
        use_case.execute(InviteToken("missing"))
