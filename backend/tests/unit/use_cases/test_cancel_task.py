"""Tests for CancelTaskUseCase (UC-035)."""
import pytest
from unittest.mock import MagicMock

from app.application.use_cases.cancel_task import CancelTaskUseCase
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import TaskStatus
from app.domain.models.task import Task
from app.domain.models.value_objects import ProjectId, TaskId


class TestCancelTaskUseCase:
    """Test suite for UC-035: Cancel Task."""

    def setup_method(self):
        self.uow = MagicMock()
        self.use_case = CancelTaskUseCase(self.uow)
        self.task = Task.create(project_id=ProjectId(), title="Task")
        self.uow.tasks.find_by_id.return_value = self.task

    def test_cancels_task(self):
        """Cancels task and commits."""
        result = self.use_case.execute(self.task.id)

        assert result.status == TaskStatus.CANCELLED
        self.uow.tasks.save.assert_called_once()
        self.uow.commit.assert_called_once()

    def test_fails_if_task_missing(self):
        """Fails if task not found."""
        self.uow.tasks.find_by_id.return_value = None
        with pytest.raises(BusinessRuleViolation):
            self.use_case.execute(TaskId())
