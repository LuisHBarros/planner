"""Tests for ProjectInvite entity."""
from datetime import datetime, timedelta, timezone

from app.domain.models.project_invite import ProjectInvite
from app.domain.models.value_objects import ProjectId, InviteToken
from app.domain.models.enums import InviteStatus


def test_invite_create_normalizes_email():
    """ProjectInvite.create normalizes email."""
    invite = ProjectInvite.create(
        project_id=ProjectId(),
        email=" Test@Example.com ",
        token=InviteToken("token"),
    )
    assert invite.email == "test@example.com"
    assert invite.status == InviteStatus.PENDING


def test_invite_accept_changes_status():
    """accept marks invite accepted."""
    invite = ProjectInvite.create(
        project_id=ProjectId(),
        email="test@example.com",
        token=InviteToken("token"),
    )
    invite.accept()
    assert invite.status == InviteStatus.ACCEPTED


def test_invite_expiration_check():
    """Expired invites are detected."""
    expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    invite = ProjectInvite.create(
        project_id=ProjectId(),
        email="test@example.com",
        token=InviteToken("token"),
        expires_at=expires_at,
    )
    assert invite.is_expired() is True
