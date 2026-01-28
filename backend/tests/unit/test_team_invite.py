"""Unit tests for TeamInvite domain model (Spec 3.0)."""
from datetime import datetime, timedelta, UTC
from uuid import uuid4

from app.domain.models.team_invite import TeamInvite
from app.domain.models.enums import TeamMemberRole


def test_team_invite_create_default_expiry():
    """Create sets default expiry to 7 days from now."""
    team_id = uuid4()
    created_by = uuid4()
    before = datetime.now(UTC)

    invite = TeamInvite.create(
        team_id=team_id,
        role=TeamMemberRole.MEMBER,
        created_by=created_by,
    )

    after = datetime.now(UTC)
    assert invite.id is not None
    assert invite.team_id == team_id
    assert invite.role == TeamMemberRole.MEMBER
    assert invite.created_by == created_by
    assert invite.used_at is None
    assert invite.token is not None
    assert len(invite.token) > 0
    assert before + timedelta(days=6) <= invite.expires_at <= after + timedelta(days=8)


def test_team_invite_create_with_custom_token_and_expiry():
    """Create accepts optional token and expires_at."""
    team_id = uuid4()
    created_by = uuid4()
    custom_token = "custom-token-123"
    custom_expiry = datetime.now(UTC) + timedelta(hours=24)

    invite = TeamInvite.create(
        team_id=team_id,
        role=TeamMemberRole.MANAGER,
        created_by=created_by,
        token=custom_token,
        expires_at=custom_expiry,
    )

    assert invite.token == custom_token
    assert invite.expires_at == custom_expiry


def test_team_invite_is_valid_when_fresh():
    """is_valid returns True when not used and not expired."""
    invite = TeamInvite.create(
        team_id=uuid4(),
        role=TeamMemberRole.MEMBER,
        created_by=uuid4(),
        expires_at=datetime.now(UTC) + timedelta(days=1),
    )
    assert invite.is_valid() is True


def test_team_invite_is_valid_false_when_expired():
    """is_valid returns False when past expires_at."""
    invite = TeamInvite(
        id=uuid4(),
        team_id=uuid4(),
        role=TeamMemberRole.MEMBER,
        token="t",
        expires_at=datetime.now(UTC) - timedelta(seconds=1),
        created_by=uuid4(),
        created_at=datetime.now(UTC),
        used_at=None,
    )
    assert invite.is_valid() is False


def test_team_invite_is_valid_false_when_used():
    """is_valid returns False after mark_used."""
    invite = TeamInvite.create(
        team_id=uuid4(),
        role=TeamMemberRole.MEMBER,
        created_by=uuid4(),
        expires_at=datetime.now(UTC) + timedelta(days=1),
    )
    invite.mark_used()
    assert invite.is_valid() is False
    assert invite.used_at is not None
