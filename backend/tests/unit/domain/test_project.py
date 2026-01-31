"""Tests for Project entity."""
from app.domain.models.project import Project
from app.domain.models.value_objects import UserId
from app.domain.models.enums import ProjectStatus


def test_project_create_sets_defaults():
    """Project.create sets status and strips name."""
    manager_id = UserId()
    project = Project.create(name="  Test Project  ", created_by=manager_id)
    assert project.name == "Test Project"
    assert project.created_by == manager_id
    assert project.status == ProjectStatus.ACTIVE


def test_project_manager_check():
    """Project.is_manager validates manager identity."""
    manager_id = UserId()
    project = Project.create(name="Test", created_by=manager_id)
    assert project.is_manager(manager_id) is True
    assert project.is_manager(UserId()) is False
