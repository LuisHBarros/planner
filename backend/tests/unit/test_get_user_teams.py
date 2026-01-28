"""Unit tests for GetUserTeamsUseCase (Spec 3.0 /me/teams)."""
from uuid import uuid4

from app.application.use_cases.get_user_teams import GetUserTeamsUseCase
from app.domain.models.team import Team
from app.domain.models.team_member import TeamMember
from app.domain.models.enums import TeamMemberRole


class _InMemoryMemberRepo:
    def __init__(self):
        self.members = []

    def save(self, member):
        self.members.append(member)

    def find_by_user_id(self, user_id):
        return [m for m in self.members if m.user_id == user_id]

    def find_by_team_id(self, team_id):
        return [m for m in self.members if m.team_id == team_id]


class _InMemoryTeamRepo:
    def __init__(self):
        self.teams = {}

    def save(self, team):
        self.teams[team.id] = team

    def find_by_id(self, team_id):
        return self.teams.get(team_id)


def test_get_user_teams_returns_teams_user_belongs_to():
    """Execute returns all teams the user is a member of."""
    member_repo = _InMemoryMemberRepo()
    team_repo = _InMemoryTeamRepo()

    user_id = uuid4()
    team_a = Team.create(company_id=uuid4(), name="Team A")
    team_b = Team.create(company_id=uuid4(), name="Team B")
    team_repo.save(team_a)
    team_repo.save(team_b)

    member_a = TeamMember.join(user_id=user_id, team_id=team_a.id, role=TeamMemberRole.MEMBER)
    member_b = TeamMember.join(user_id=user_id, team_id=team_b.id, role=TeamMemberRole.MANAGER)
    member_repo.save(member_a)
    member_repo.save(member_b)

    use_case = GetUserTeamsUseCase(
        team_member_repository=member_repo,
        team_repository=team_repo,
    )

    teams = use_case.execute(user_id=user_id)

    assert len(teams) == 2
    team_ids = {t.id for t in teams}
    assert team_a.id in team_ids
    assert team_b.id in team_ids
    names = {t.name for t in teams}
    assert "Team A" in names
    assert "Team B" in names


def test_get_user_teams_empty_when_no_membership():
    """Execute returns empty list when user has no team memberships."""
    member_repo = _InMemoryMemberRepo()
    team_repo = _InMemoryTeamRepo()

    use_case = GetUserTeamsUseCase(
        team_member_repository=member_repo,
        team_repository=team_repo,
    )

    teams = use_case.execute(user_id=uuid4())

    assert teams == []


def test_get_user_teams_ignores_missing_team_entity():
    """If a membership references a deleted team, that team is omitted from the list."""
    member_repo = _InMemoryMemberRepo()
    team_repo = _InMemoryTeamRepo()

    user_id = uuid4()
    team_that_exists = Team.create(company_id=uuid4(), name="Exists")
    team_repo.save(team_that_exists)

    member_existing = TeamMember.join(
        user_id=user_id, team_id=team_that_exists.id, role=TeamMemberRole.MEMBER
    )
    member_repo.save(member_existing)

    # Membership for a team we never persist (simulates deleted team)
    deleted_team_id = uuid4()
    member_orphan = TeamMember(
        id=uuid4(),
        user_id=user_id,
        team_id=deleted_team_id,
        role=TeamMemberRole.MEMBER,
        joined_at=member_existing.joined_at,
    )
    member_repo.save(member_orphan)

    use_case = GetUserTeamsUseCase(
        team_member_repository=member_repo,
        team_repository=team_repo,
    )

    teams = use_case.execute(user_id=user_id)

    assert len(teams) == 1
    assert teams[0].id == team_that_exists.id
    assert teams[0].name == "Exists"
