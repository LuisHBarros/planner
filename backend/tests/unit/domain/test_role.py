"""Tests for Role entity."""
from app.domain.models.role import Role
from app.domain.models.value_objects import ProjectId


def test_role_create_strips_name():
    """Role.create normalizes name."""
    role = Role.create(
        project_id=ProjectId(),
        name="  Designer  ",
        description="UI/UX",
    )
    assert role.name == "Designer"
    assert role.description == "UI/UX"
