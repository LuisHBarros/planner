"""Tests for AbandonTaskUseCase (UC-041)."""
import pytest
from unittest.mock import Mock, MagicMock

from app.application.dtos.task_dtos import AbandonTaskInput
from app.application.use_cases.abandon_task import AbandonTaskUseCase
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import AbandonmentType, TaskStatus
from app.domain.models.task import Task
from app.domain.models.value_objects import ProjectId, UserId


class TestAbandonTaskUseCase:
    """Test suite for UC-041: Abandon Task."""

    def setup_method(self):
        self.uow = MagicMock()
        self.event_bus = Mock()
        self.use_case = AbandonTaskUseCase(self.uow, self.event_bus)
        self.user_id = UserId()
        self.task = Task.create(project_id=ProjectId(), title="Task")
        self.task.status = TaskStatus.DOING
        self.task.assigned_to = self.user_id
        self.uow.tasks.find_by_id.return_value = self.task

    def test_abandons_task(self):
        """Abandons task and records abandonment."""
        input_dto = AbandonTaskInput(
            task_id=self.task.id,
            user_id=self.user_id,
            abandonment_type=AbandonmentType.VOLUNTARY,
            note="Busy",
        )

        result = self.use_case.execute(input_dto)

        assert result.status == TaskStatus.TODO
        assert result.assigned_to is None
        self.uow.task_abandonments.save.assert_called_once()
        self.uow.commit.assert_called_once()
        self.event_bus.emit.assert_called_once()

    def test_fails_if_task_not_assigned_to_user(self):
        """Fails if task assigned to different user."""
        input_dto = AbandonTaskInput(
            task_id=self.task.id,
            user_id=UserId(),
            abandonment_type=AbandonmentType.VOLUNTARY,
        )

        with pytest.raises(BusinessRuleViolation):
            self.use_case.execute(input_dto)
