"""Tests for User entity."""
from app.domain.models.user import User


def test_user_create_normalizes_email_and_name():
    """User.create lowercases email and strips whitespace."""
    user = User.create(email=" Test@Example.com ", name="  Alice  ")
    assert user.email == "test@example.com"
    assert user.name == "Alice"
    assert user.id is not None
