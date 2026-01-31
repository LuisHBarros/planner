"""Tests for TaskDependency entity."""
from app.domain.models.task_dependency import TaskDependency
from app.domain.models.value_objects import TaskId
from app.domain.models.enums import DependencyType


def test_task_dependency_create_sets_type():
    """TaskDependency.create defaults to finish_to_start."""
    dependency = TaskDependency.create(
        task_id=TaskId(),
        depends_on_id=TaskId(),
    )
    assert dependency.dependency_type == DependencyType.FINISH_TO_START
