"""Tests for workload blocking on task selection."""
import pytest
from unittest.mock import Mock, MagicMock

from app.application.dtos.task_dtos import SelectTaskInput
from app.application.use_cases.select_task import SelectTaskUseCase
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import MemberLevel, TaskStatus
from app.domain.models.project_member import ProjectMember
from app.domain.models.task import Task
from app.domain.models.value_objects import ProjectId, UserId


def test_select_task_blocks_impossible_workload():
    """Selecting a task must not exceed IMPOSSIBLE workload."""
    uow = MagicMock()
    event_bus = Mock()
    use_case = SelectTaskUseCase(uow, event_bus)
    user_id = UserId()
    project_id = ProjectId()
    task = Task.create(project_id=project_id, title="Task")
    task.difficulty = 10
    uow.tasks.find_by_id.return_value = task
    member = ProjectMember.create_member(
        project_id=project_id,
        user_id=user_id,
        level=MemberLevel.MID,
        base_capacity=10,
    )
    uow.project_members.find_by_project_and_user.return_value = member
    existing = Task.create(project_id=project_id, title="Existing")
    existing.status = TaskStatus.DOING
    existing.assigned_to = user_id
    existing.difficulty = 6
    uow.tasks.list_by_project.return_value = [existing]

    with pytest.raises(BusinessRuleViolation):
        use_case.execute(SelectTaskInput(task_id=task.id, user_id=user_id))
