"""Tests for employee-related use cases."""
import pytest
from unittest.mock import MagicMock

from app.application.use_cases.change_employee_role import ChangeEmployeeRoleUseCase
from app.application.use_cases.get_employee_workload import GetEmployeeWorkloadUseCase
from app.application.use_cases.list_team import ListTeamUseCase
from app.application.use_cases.resign_from_project import ResignFromProjectUseCase
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import MemberLevel, TaskStatus, WorkloadStatus
from app.domain.models.project_member import ProjectMember
from app.domain.models.task import Task
from app.domain.models.value_objects import ProjectId, RoleId, UserId


def test_resign_from_project_unassigns_tasks():
    """Resigns and unassigns tasks."""
    uow = MagicMock()
    project_id = ProjectId()
    user_id = UserId()
    member = ProjectMember.create_member(
        project_id=project_id,
        user_id=user_id,
        level=MemberLevel.MID,
        base_capacity=10,
    )
    uow.project_members.find_by_project_and_user.return_value = member
    task = Task.create(project_id=project_id, title="Task")
    task.status = TaskStatus.DOING
    task.assigned_to = user_id
    uow.tasks.list_by_project.return_value = [task]
    use_case = ResignFromProjectUseCase(uow)

    use_case.execute(project_id, user_id)

    uow.tasks.save.assert_called_once()
    uow.task_abandonments.save.assert_called_once()
    uow.commit.assert_called_once()


def test_list_team_returns_members():
    """Lists project members."""
    uow = MagicMock()
    member = ProjectMember.create_member(
        project_id=ProjectId(),
        user_id=UserId(),
        level=MemberLevel.MID,
        base_capacity=10,
    )
    uow.project_members.list_by_project.return_value = [member]
    use_case = ListTeamUseCase(uow)

    result = use_case.execute(member.project_id)

    assert result[0].user_id == member.user_id


def test_get_employee_workload_computes_status():
    """Computes workload from doing tasks."""
    uow = MagicMock()
    project_id = ProjectId()
    user_id = UserId()
    member = ProjectMember.create_member(
        project_id=project_id,
        user_id=user_id,
        level=MemberLevel.MID,
        base_capacity=10,
    )
    uow.project_members.find_by_project_and_user.return_value = member
    task = Task.create(project_id=project_id, title="Task")
    task.status = TaskStatus.DOING
    task.assigned_to = user_id
    task.difficulty = 8
    uow.tasks.list_by_project.return_value = [task]
    use_case = GetEmployeeWorkloadUseCase(uow)

    result = use_case.execute(project_id, user_id)

    assert result.status == WorkloadStatus.HEALTHY


def test_change_employee_role_updates_member():
    """Updates member role."""
    uow = MagicMock()
    project_id = ProjectId()
    user_id = UserId()
    member = ProjectMember.create_member(
        project_id=project_id,
        user_id=user_id,
        level=MemberLevel.MID,
        base_capacity=10,
    )
    uow.project_members.find_by_project_and_user.return_value = member
    use_case = ChangeEmployeeRoleUseCase(uow)
    new_role = RoleId()

    use_case.execute(project_id, user_id, new_role)

    assert member.role_id == new_role
    uow.project_members.save.assert_called_once()
    uow.commit.assert_called_once()


def test_get_employee_workload_fails_if_missing_member():
    """Fails if member not found."""
    uow = MagicMock()
    uow.project_members.find_by_project_and_user.return_value = None
    use_case = GetEmployeeWorkloadUseCase(uow)

    with pytest.raises(BusinessRuleViolation):
        use_case.execute(ProjectId(), UserId())
