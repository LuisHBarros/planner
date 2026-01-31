"""Tests for CompleteTaskUseCase (UC-045)."""
import pytest
from unittest.mock import Mock, MagicMock

from app.application.use_cases.complete_task import CompleteTaskUseCase
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import TaskStatus
from app.domain.models.task import Task
from app.domain.models.value_objects import ProjectId, TaskId


class TestCompleteTaskUseCase:
    """Test suite for UC-045: Complete Task."""

    def setup_method(self):
        self.uow = MagicMock()
        self.event_bus = Mock()
        self.use_case = CompleteTaskUseCase(self.uow, self.event_bus)
        self.task = Task.create(project_id=ProjectId(), title="Task")
        self.task.status = TaskStatus.DOING
        self.uow.tasks.find_by_id.return_value = self.task

    def test_completes_task(self):
        """Completes task and emits event."""
        result = self.use_case.execute(self.task.id)

        assert result.status == TaskStatus.DONE
        self.uow.tasks.save.assert_called_once()
        self.uow.commit.assert_called_once()
        self.event_bus.emit.assert_called_once()

    def test_fails_if_task_missing(self):
        """Fails if task not found."""
        self.uow.tasks.find_by_id.return_value = None
        with pytest.raises(BusinessRuleViolation):
            self.use_case.execute(TaskId())
