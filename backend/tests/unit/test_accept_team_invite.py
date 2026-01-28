"""Unit tests for AcceptTeamInviteUseCase (Spec 3.0)."""
from datetime import datetime, timedelta, UTC
from uuid import uuid4

import pytest

from app.application.use_cases.accept_team_invite import AcceptTeamInviteUseCase
from app.domain.models.team import Team
from app.domain.models.user import User
from app.domain.models.team_invite import TeamInvite
from app.domain.models.enums import TeamMemberRole
from app.domain.exceptions import BusinessRuleViolation


class _InMemoryInviteRepo:
    def __init__(self):
        self.by_token = {}

    def save(self, invite):
        self.by_token[invite.token] = invite

    def find_by_token(self, token):
        return self.by_token.get(token)


class _InMemoryMemberRepo:
    def __init__(self):
        self.members = []

    def save(self, member):
        self.members.append(member)

    def find_by_user_id(self, user_id):
        return [m for m in self.members if m.user_id == user_id]

    def find_by_team_id(self, team_id):
        return [m for m in self.members if m.team_id == team_id]


class _InMemoryUserRepo:
    def __init__(self):
        self.users = {}

    def save(self, user):
        self.users[user.id] = user

    def find_by_id(self, user_id):
        return self.users.get(user_id)

    def find_by_email(self, email):
        for u in self.users.values():
            if u.email == email:
                return u
        return None


class _InMemoryTeamRepo:
    def __init__(self):
        self.teams = {}

    def save(self, team):
        self.teams[team.id] = team

    def find_by_id(self, team_id):
        return self.teams.get(team_id)


def test_accept_team_invite_success():
    """Accepting a valid invite creates TeamMember and marks invite used."""
    invite_repo = _InMemoryInviteRepo()
    member_repo = _InMemoryMemberRepo()
    user_repo = _InMemoryUserRepo()
    team_repo = _InMemoryTeamRepo()

    team = Team.create(company_id=uuid4(), name="Dev Team")
    team_repo.save(team)
    user = User.create("dev@example.com", "Dev User")
    user_repo.save(user)

    invite = TeamInvite.create(
        team_id=team.id,
        role=TeamMemberRole.BACKEND,
        created_by=uuid4(),
    )
    invite_repo.save(invite)

    use_case = AcceptTeamInviteUseCase(
        invite_repository=invite_repo,
        member_repository=member_repo,
        user_repository=user_repo,
        team_repository=team_repo,
    )

    member = use_case.execute(token=invite.token, user_id=user.id)

    assert member.user_id == user.id
    assert member.team_id == team.id
    assert member.role == TeamMemberRole.BACKEND
    assert member.joined_at is not None
    assert len(member_repo.members) == 1
    assert invite.used_at is not None


def test_accept_team_invite_token_not_found():
    """Accepting with unknown token raises invite_not_found."""
    invite_repo = _InMemoryInviteRepo()
    member_repo = _InMemoryMemberRepo()
    user_repo = _InMemoryUserRepo()
    team_repo = _InMemoryTeamRepo()
    user = User.create("u@x.com", "U")
    user_repo.save(user)

    use_case = AcceptTeamInviteUseCase(
        invite_repository=invite_repo,
        member_repository=member_repo,
        user_repository=user_repo,
        team_repository=team_repo,
    )

    with pytest.raises(BusinessRuleViolation) as exc_info:
        use_case.execute(token="nonexistent-token", user_id=user.id)

    assert exc_info.value.code == "invite_not_found"
    assert len(member_repo.members) == 0


def test_accept_team_invite_expired():
    """Accepting an expired invite raises invite_invalid."""
    invite_repo = _InMemoryInviteRepo()
    member_repo = _InMemoryMemberRepo()
    user_repo = _InMemoryUserRepo()
    team_repo = _InMemoryTeamRepo()

    team = Team.create(company_id=uuid4(), name="T")
    team_repo.save(team)
    user = User.create("u@x.com", "U")
    user_repo.save(user)

    invite = TeamInvite(
        id=uuid4(),
        team_id=team.id,
        role=TeamMemberRole.MEMBER,
        token="expired-token",
        expires_at=datetime.now(UTC) - timedelta(days=1),
        created_by=uuid4(),
        created_at=datetime.now(UTC),
        used_at=None,
    )
    invite_repo.save(invite)

    use_case = AcceptTeamInviteUseCase(
        invite_repository=invite_repo,
        member_repository=member_repo,
        user_repository=user_repo,
        team_repository=team_repo,
    )

    with pytest.raises(BusinessRuleViolation) as exc_info:
        use_case.execute(token="expired-token", user_id=user.id)

    assert exc_info.value.code == "invite_invalid"
    assert len(member_repo.members) == 0


def test_accept_team_invite_user_not_found():
    """Accepting with non-existent user raises user_not_found."""
    invite_repo = _InMemoryInviteRepo()
    member_repo = _InMemoryMemberRepo()
    user_repo = _InMemoryUserRepo()
    team_repo = _InMemoryTeamRepo()

    team = Team.create(company_id=uuid4(), name="T")
    team_repo.save(team)
    invite = TeamInvite.create(team_id=team.id, role=TeamMemberRole.MEMBER, created_by=uuid4())
    invite_repo.save(invite)

    use_case = AcceptTeamInviteUseCase(
        invite_repository=invite_repo,
        member_repository=member_repo,
        user_repository=user_repo,
        team_repository=team_repo,
    )

    with pytest.raises(BusinessRuleViolation) as exc_info:
        use_case.execute(token=invite.token, user_id=uuid4())

    assert exc_info.value.code == "user_not_found"
    assert len(member_repo.members) == 0
