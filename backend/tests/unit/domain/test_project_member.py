"""Tests for ProjectMember entity."""
from app.domain.models.project_member import ProjectMember
from app.domain.models.value_objects import ProjectId, UserId
from app.domain.models.enums import MemberLevel


def test_create_member_sets_defaults():
    """ProjectMember.create_member sets defaults."""
    member = ProjectMember.create_member(
        project_id=ProjectId(),
        user_id=UserId(),
        level=MemberLevel.MID,
        base_capacity=10,
    )
    assert member.is_manager is False
    assert member.level == MemberLevel.MID
    assert member.base_capacity == 10


def test_create_manager_sets_manager_flag():
    """ProjectMember.create_manager marks manager role."""
    member = ProjectMember.create_manager(
        project_id=ProjectId(),
        user_id=UserId(),
    )
    assert member.is_manager is True
