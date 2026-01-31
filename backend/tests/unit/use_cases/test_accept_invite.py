"""Tests for AcceptInviteUseCase (UC-022)."""
import pytest
from unittest.mock import Mock, MagicMock

from app.application.dtos.project_dtos import AcceptInviteInput
from app.application.use_cases.accept_invite import AcceptInviteUseCase
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import MemberLevel
from app.domain.models.project_invite import ProjectInvite
from app.domain.models.value_objects import InviteToken, ProjectId, UserId


class TestAcceptInviteUseCase:
    """Test suite for UC-022: Accept Invite."""

    def setup_method(self):
        self.uow = MagicMock()
        self.event_bus = Mock()
        self.use_case = AcceptInviteUseCase(self.uow, self.event_bus)
        self.invite = ProjectInvite.create(
            project_id=ProjectId(),
            email="invitee@example.com",
            token=InviteToken("token"),
        )
        self.uow.project_invites.find_by_token.return_value = self.invite

    def test_accepts_invite_and_creates_member(self):
        """Accepts invite and creates member."""
        input_dto = AcceptInviteInput(
            token=InviteToken("token"),
            user_id=UserId(),
            level=MemberLevel.MID,
            base_capacity=10,
        )

        result = self.use_case.execute(input_dto)

        assert result.status.value == "accepted"
        self.uow.project_members.save.assert_called_once()
        self.uow.commit.assert_called_once()
        self.event_bus.emit.assert_called_once()

    def test_fails_if_invite_missing(self):
        """Fails if invite not found."""
        self.uow.project_invites.find_by_token.return_value = None
        input_dto = AcceptInviteInput(
            token=InviteToken("missing"),
            user_id=UserId(),
            level=MemberLevel.MID,
            base_capacity=10,
        )

        with pytest.raises(BusinessRuleViolation):
            self.use_case.execute(input_dto)
