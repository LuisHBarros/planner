"""Tests for FireEmployeeUseCase (UC-051)."""
import pytest
from unittest.mock import MagicMock

from app.application.use_cases.fire_employee import FireEmployeeUseCase
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import TaskStatus
from app.domain.models.enums import MemberLevel
from app.domain.models.project_member import ProjectMember
from app.domain.models.task import Task
from app.domain.models.value_objects import ProjectId, UserId


class TestFireEmployeeUseCase:
    """Test suite for UC-051: Fire Employee."""

    def setup_method(self):
        self.uow = MagicMock()
        self.use_case = FireEmployeeUseCase(self.uow)
        self.project_id = ProjectId()
        self.user_id = UserId()
        self.member = ProjectMember.create_member(
            project_id=self.project_id,
            user_id=self.user_id,
            level=MemberLevel.MID,
            base_capacity=10,
        )
        self.uow.project_members.find_by_project_and_user.return_value = self.member

    def test_fires_employee_and_unassigns_tasks(self):
        """Unassigns tasks and records abandonments."""
        task = Task.create(project_id=self.project_id, title="Task")
        task.status = TaskStatus.DOING
        task.assigned_to = self.user_id
        self.uow.tasks.list_by_project.return_value = [task]

        self.use_case.execute(self.project_id, self.user_id)

        self.uow.tasks.save.assert_called_once()
        self.uow.task_abandonments.save.assert_called_once()
        self.uow.commit.assert_called_once()

    def test_fails_if_member_missing(self):
        """Fails if project member not found."""
        self.uow.project_members.find_by_project_and_user.return_value = None
        with pytest.raises(BusinessRuleViolation):
            self.use_case.execute(self.project_id, self.user_id)
