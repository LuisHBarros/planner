"""Tests for value objects."""
from datetime import datetime, timezone
from uuid import UUID

from app.domain.models.value_objects import (
    InviteToken,
    ProjectId,
    ProjectMemberId,
    RoleId,
    TaskId,
    UserId,
    UtcDateTime,
)


def test_ids_generate_uuid_by_default():
    """Default constructors generate UUIDs."""
    assert isinstance(UserId().value, UUID)
    assert isinstance(ProjectId().value, UUID)
    assert isinstance(RoleId().value, UUID)
    assert isinstance(TaskId().value, UUID)
    assert isinstance(ProjectMemberId().value, UUID)


def test_invite_token_str():
    """InviteToken returns its raw value."""
    token = InviteToken("abc123")
    assert str(token) == "abc123"


def test_utc_datetime_defaults_to_utc_now():
    """UtcDateTime defaults to an aware UTC datetime."""
    value = UtcDateTime().value
    assert value.tzinfo == timezone.utc


def test_utc_datetime_makes_naive_utc():
    """Naive datetimes are coerced to UTC."""
    naive = datetime(2024, 1, 1, 12, 0, 0)
    utc_value = UtcDateTime(naive).value
    assert utc_value.tzinfo == timezone.utc


def test_utc_datetime_comparisons():
    """UtcDateTime supports ordering comparisons."""
    first = UtcDateTime(datetime(2024, 1, 1, tzinfo=timezone.utc))
    second = UtcDateTime(datetime(2024, 1, 2, tzinfo=timezone.utc))
    assert first < second
    assert first <= second
    assert second > first
    assert second >= first
