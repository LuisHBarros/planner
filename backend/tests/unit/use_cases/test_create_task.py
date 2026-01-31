"""Tests for CreateTaskUseCase (UC-030)."""
import pytest
from unittest.mock import Mock, MagicMock

from app.application.dtos.task_dtos import CreateTaskInput
from app.application.use_cases.create_task import CreateTaskUseCase
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.project import Project
from app.domain.models.value_objects import ProjectId, UserId


class TestCreateTaskUseCase:
    """Test suite for UC-030: Create Task."""

    def setup_method(self):
        self.uow = MagicMock()
        self.event_bus = Mock()
        self.use_case = CreateTaskUseCase(self.uow, self.event_bus)
        self.project = Project.create(name="Proj", created_by=UserId())
        self.uow.projects.find_by_id.return_value = self.project

    def test_creates_task(self):
        """Creates task and commits."""
        input_dto = CreateTaskInput(
            project_id=self.project.id,
            title="Build API",
        )

        result = self.use_case.execute(input_dto)

        assert result.title == "Build API"
        self.uow.tasks.save.assert_called_once()
        self.uow.commit.assert_called_once()
        self.event_bus.emit.assert_called_once()

    def test_fails_if_project_missing(self):
        """Fails if project not found."""
        self.uow.projects.find_by_id.return_value = None
        input_dto = CreateTaskInput(
            project_id=ProjectId(),
            title="Build API",
        )

        with pytest.raises(BusinessRuleViolation):
            self.use_case.execute(input_dto)
