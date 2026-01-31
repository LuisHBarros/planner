"""Tests for task-related use cases."""
import pytest
from unittest.mock import MagicMock

from app.application.dtos.task_dtos import (
    CalculateProgressInput,
    SetTaskDifficultyInput,
    TaskDependencyInput,
    TaskReportInput,
)
from app.application.use_cases.add_task_dependency import AddTaskDependencyUseCase
from app.application.use_cases.add_task_report import AddTaskReportUseCase
from app.application.use_cases.calculate_progress_llm import CalculateProgressLlmUseCase
from app.application.use_cases.calculate_task_difficulty_llm import CalculateTaskDifficultyLlmUseCase
from app.application.use_cases.remove_from_task import RemoveFromTaskUseCase
from app.application.use_cases.remove_task_dependency import RemoveTaskDependencyUseCase
from app.application.use_cases.set_task_difficulty_manual import SetTaskDifficultyManualUseCase
from app.application.use_cases.update_progress_manual import UpdateProgressManualUseCase
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import ProgressSource, TaskStatus
from app.domain.models.task import Task
from app.domain.models.value_objects import ProjectId, TaskId, UserId


def test_set_task_difficulty_manual_updates_task():
    """Updates task difficulty."""
    uow = MagicMock()
    task = Task.create(project_id=ProjectId(), title="Task")
    uow.tasks.find_by_id.return_value = task
    use_case = SetTaskDifficultyManualUseCase(uow)

    result = use_case.execute(SetTaskDifficultyInput(task_id=task.id, difficulty=5))

    assert result.difficulty == 5
    uow.tasks.save.assert_called_once()
    uow.commit.assert_called_once()


def test_calculate_task_difficulty_llm_sets_value():
    """Sets difficulty from LLM."""
    uow = MagicMock()
    task = Task.create(project_id=ProjectId(), title="Task")
    uow.tasks.find_by_id.return_value = task
    uow.llm_service.calculate_task_difficulty.return_value = 7
    use_case = CalculateTaskDifficultyLlmUseCase(uow)

    result = use_case.execute(task.id)

    assert result.difficulty == 7
    uow.tasks.save.assert_called_once()
    uow.commit.assert_called_once()


def test_add_and_remove_task_dependency():
    """Adds and removes task dependency."""
    uow = MagicMock()
    add_use_case = AddTaskDependencyUseCase(uow)
    remove_use_case = RemoveTaskDependencyUseCase(uow)
    task_id = TaskId()
    depends_on_id = TaskId()

    add_use_case.execute(TaskDependencyInput(task_id=task_id, depends_on_id=depends_on_id))
    remove_use_case.execute(TaskDependencyInput(task_id=task_id, depends_on_id=depends_on_id))

    uow.task_dependencies.save.assert_called_once()
    uow.task_dependencies.delete.assert_called_once()
    assert uow.commit.call_count == 2


def test_add_task_report_creates_report():
    """Creates task report."""
    uow = MagicMock()
    use_case = AddTaskReportUseCase(uow)
    input_dto = TaskReportInput(
        task_id=TaskId(),
        author_id=UserId(),
        progress=30,
        source=ProgressSource.MANUAL,
        note="Update",
    )

    result = use_case.execute(input_dto)

    assert result.progress == 30
    uow.task_reports.save.assert_called_once()
    uow.commit.assert_called_once()


def test_calculate_progress_llm_creates_report():
    """Calculates progress and stores report."""
    uow = MagicMock()
    task = Task.create(project_id=ProjectId(), title="Task")
    uow.tasks.find_by_id.return_value = task
    uow.llm_service.calculate_task_progress.return_value = 55
    use_case = CalculateProgressLlmUseCase(uow)

    result = use_case.execute(CalculateProgressInput(task_id=task.id, author_id=UserId()))

    assert result.progress == 55
    uow.task_reports.save.assert_called_once()
    uow.commit.assert_called_once()


def test_update_progress_manual_creates_report():
    """Creates manual progress report."""
    uow = MagicMock()
    use_case = UpdateProgressManualUseCase(uow)
    input_dto = TaskReportInput(
        task_id=TaskId(),
        author_id=UserId(),
        progress=70,
        source=ProgressSource.MANUAL,
    )

    result = use_case.execute(input_dto)

    assert result.progress == 70
    uow.task_reports.save.assert_called_once()
    uow.commit.assert_called_once()


def test_remove_from_task_unassigns():
    """Removes user from task."""
    uow = MagicMock()
    task = Task.create(project_id=ProjectId(), title="Task")
    task.status = TaskStatus.DOING
    user_id = UserId()
    task.assigned_to = user_id
    uow.tasks.find_by_id.return_value = task
    use_case = RemoveFromTaskUseCase(uow)

    result = use_case.execute(task.id, user_id)

    assert result.assigned_to is None
    uow.task_assignment_history.save.assert_called_once()
    uow.commit.assert_called_once()


def test_remove_from_task_fails_when_not_assigned():
    """Fails if task not assigned to user."""
    uow = MagicMock()
    task = Task.create(project_id=ProjectId(), title="Task")
    uow.tasks.find_by_id.return_value = task
    use_case = RemoveFromTaskUseCase(uow)

    with pytest.raises(BusinessRuleViolation):
        use_case.execute(task.id, UserId())
