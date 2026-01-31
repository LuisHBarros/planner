"""Tests for SelectTaskUseCase (UC-040)."""
import pytest
from unittest.mock import Mock, MagicMock

from app.application.dtos.task_dtos import SelectTaskInput
from app.application.use_cases.select_task import SelectTaskUseCase
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import MemberLevel, TaskStatus
from app.domain.models.project_member import ProjectMember
from app.domain.models.task import Task
from app.domain.models.value_objects import ProjectId, UserId


class TestSelectTaskUseCase:
    """Test suite for UC-040: Select Task."""

    def setup_method(self):
        self.uow = MagicMock()
        self.event_bus = Mock()
        self.use_case = SelectTaskUseCase(self.uow, self.event_bus)
        self.user_id = UserId()
        self.project_id = ProjectId()
        self.task = Task.create(project_id=self.project_id, title="Task")
        self.uow.tasks.find_by_id.return_value = self.task
        self.member = ProjectMember.create_member(
            project_id=self.project_id,
            user_id=self.user_id,
            level=MemberLevel.MID,
            base_capacity=10,
        )
        self.uow.project_members.find_by_project_and_user.return_value = self.member

    def test_selects_task_successfully(self):
        """Selects task and assigns user."""
        self.task.difficulty = 3
        self.uow.tasks.list_by_project.return_value = []
        input_dto = SelectTaskInput(task_id=self.task.id, user_id=self.user_id)

        result = self.use_case.execute(input_dto)

        assert result.status == TaskStatus.DOING
        assert result.assigned_to == self.user_id
        self.uow.task_assignment_history.save.assert_called_once()
        self.uow.commit.assert_called_once()

    def test_fails_if_difficulty_not_set(self):
        """Cannot select task without difficulty."""
        self.task.difficulty = None
        self.uow.tasks.list_by_project.return_value = []
        input_dto = SelectTaskInput(task_id=self.task.id, user_id=self.user_id)

        with pytest.raises(BusinessRuleViolation):
            self.use_case.execute(input_dto)

    def test_fails_if_manager(self):
        """Managers cannot claim tasks."""
        self.task.difficulty = 3
        self.member.is_manager = True
        self.uow.tasks.list_by_project.return_value = []
        input_dto = SelectTaskInput(task_id=self.task.id, user_id=self.user_id)

        with pytest.raises(BusinessRuleViolation):
            self.use_case.execute(input_dto)

    def test_fails_if_workload_impossible(self):
        """Workload cannot become IMPOSSIBLE."""
        self.task.difficulty = 10
        existing = Task.create(project_id=self.project_id, title="Existing")
        existing.status = TaskStatus.DOING
        existing.assigned_to = self.user_id
        existing.difficulty = 6
        self.uow.tasks.list_by_project.return_value = [existing]
        input_dto = SelectTaskInput(task_id=self.task.id, user_id=self.user_id)

        with pytest.raises(BusinessRuleViolation):
            self.use_case.execute(input_dto)
