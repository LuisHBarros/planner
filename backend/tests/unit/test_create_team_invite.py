"""Unit tests for CreateTeamInviteUseCase (Spec 3.0)."""
from datetime import datetime, timedelta, UTC
from uuid import uuid4

import pytest

from app.application.use_cases.create_team_invite import CreateTeamInviteUseCase
from app.domain.models.team import Team
from app.domain.models.enums import TeamMemberRole
from app.domain.exceptions import BusinessRuleViolation


class _InMemoryTeamRepo:
    def __init__(self):
        self.teams = {}

    def save(self, team):
        self.teams[team.id] = team

    def find_by_id(self, team_id):
        return self.teams.get(team_id)


class _InMemoryInviteRepo:
    def __init__(self):
        self.invites = []

    def save(self, invite):
        self.invites.append(invite)

    def find_by_token(self, token):
        for i in self.invites:
            if i.token == token:
                return i
        return None


def test_create_team_invite_success():
    """Creating an invite for an existing team persists invite with token and role."""
    team_repo = _InMemoryTeamRepo()
    invite_repo = _InMemoryInviteRepo()

    team = Team.create(company_id=uuid4(), name="Dev Team")
    team_repo.save(team)

    use_case = CreateTeamInviteUseCase(
        team_repository=team_repo,
        invite_repository=invite_repo,
    )

    created_by = uuid4()
    invite = use_case.execute(
        team_id=team.id,
        role=TeamMemberRole.MANAGER,
        created_by=created_by,
    )

    assert invite.team_id == team.id
    assert invite.role == TeamMemberRole.MANAGER
    assert invite.created_by == created_by
    assert invite.token is not None
    assert len(invite.token) > 0
    assert invite.used_at is None
    assert invite.expires_at > datetime.now(UTC)
    assert len(invite_repo.invites) == 1
    assert invite_repo.invites[0].id == invite.id


def test_create_team_invite_with_custom_expiry():
    """Invite can be created with custom expires_at."""
    team_repo = _InMemoryTeamRepo()
    invite_repo = _InMemoryInviteRepo()

    team = Team.create(company_id=uuid4(), name="Team")
    team_repo.save(team)

    use_case = CreateTeamInviteUseCase(
        team_repository=team_repo,
        invite_repository=invite_repo,
    )

    custom_expiry = datetime.now(UTC) + timedelta(days=1)
    invite = use_case.execute(
        team_id=team.id,
        role=TeamMemberRole.MEMBER,
        created_by=uuid4(),
        expires_at=custom_expiry,
    )

    assert invite.expires_at == custom_expiry


def test_create_team_invite_team_not_found():
    """Creating an invite for non-existent team raises team_not_found."""
    team_repo = _InMemoryTeamRepo()
    invite_repo = _InMemoryInviteRepo()

    use_case = CreateTeamInviteUseCase(
        team_repository=team_repo,
        invite_repository=invite_repo,
    )

    with pytest.raises(BusinessRuleViolation) as exc_info:
        use_case.execute(
            team_id=uuid4(),
            role=TeamMemberRole.MEMBER,
            created_by=uuid4(),
        )

    assert exc_info.value.code == "team_not_found"
    assert len(invite_repo.invites) == 0
