"""Tests for MagicLink entity."""
import pytest
from datetime import datetime, timedelta, timezone

from app.domain.models.magic_link import MagicLink
from app.domain.models.value_objects import InviteToken, UserId, UtcDateTime
from app.domain.exceptions import BusinessRuleViolation


def test_magic_link_create_defaults():
    """MagicLink.create sets token and expiry."""
    link = MagicLink.create(
        token=InviteToken("token"),
        user_id=UserId(),
        expires_at=UtcDateTime(),
    )
    assert link.consumed_at is None


def test_magic_link_consume_sets_consumed_at():
    """Consume marks magic link as used."""
    expires = UtcDateTime(datetime.now(timezone.utc) + timedelta(hours=1))
    link = MagicLink.create(
        token=InviteToken("token"),
        user_id=UserId(),
        expires_at=expires,
    )
    link.consume()
    assert link.consumed_at is not None


def test_magic_link_cannot_consume_expired():
    """Expired links cannot be consumed."""
    expired = UtcDateTime(datetime.now(timezone.utc) - timedelta(hours=1))
    link = MagicLink.create(
        token=InviteToken("token"),
        user_id=UserId(),
        expires_at=expired,
    )
    with pytest.raises(BusinessRuleViolation):
        link.consume()
