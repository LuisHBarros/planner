"""Tests for PropagateScheduleUseCase (UC-061)."""
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.application.dtos.schedule_dtos import PropagateScheduleInput
from app.application.use_cases.propagate_schedule import PropagateScheduleUseCase
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.task import Task
from app.domain.models.value_objects import ProjectId, UtcDateTime, TaskId


class TestPropagateScheduleUseCase:
    """Test suite for UC-061: Propagate Schedule."""

    def setup_method(self):
        self.uow = MagicMock()
        self.use_case = PropagateScheduleUseCase(self.uow)
        self.task = Task.create(project_id=ProjectId(), title="Task")
        self.task.expected_start_date = UtcDateTime(datetime(2024, 1, 1, tzinfo=timezone.utc))
        self.task.expected_end_date = UtcDateTime(datetime(2024, 1, 2, tzinfo=timezone.utc))
        self.uow.tasks.find_by_id.return_value = self.task

    def test_propagates_schedule_and_records_history(self):
        """Updates dates and saves history."""
        input_dto = PropagateScheduleInput(task_id=self.task.id, delay_delta_seconds=86400)

        self.use_case.execute(input_dto)

        self.uow.tasks.save.assert_called_once()
        self.uow.schedule_history.save_task_history.assert_called_once()
        self.uow.commit.assert_called_once()

    def test_fails_if_task_missing(self):
        """Fails if task not found."""
        self.uow.tasks.find_by_id.return_value = None
        input_dto = PropagateScheduleInput(task_id=TaskId(), delay_delta_seconds=60)

        with pytest.raises(BusinessRuleViolation):
            self.use_case.execute(input_dto)
