"""Unit tests for UC-030: Get Delay Chain Use Case."""
from datetime import datetime, timedelta, UTC
from uuid import uuid4
from typing import Dict, List, Optional
from uuid import UUID

import pytest

from app.domain.models.task import Task
from app.domain.models.schedule_history import ScheduleHistory
from app.domain.models.enums import TaskStatus, TaskPriority, ScheduleChangeReason
from app.application.use_cases.get_delay_chain import GetDelayChainUseCase
from app.domain.exceptions import BusinessRuleViolation


class _InMemoryTaskRepo:
    """In-memory task repository for testing."""

    def __init__(self):
        self.tasks: Dict[UUID, Task] = {}

    def save(self, task: Task) -> None:
        self.tasks[task.id] = task

    def find_by_id(self, task_id: UUID) -> Optional[Task]:
        return self.tasks.get(task_id)


class _InMemoryScheduleHistoryRepo:
    """In-memory schedule history repository for testing."""

    def __init__(self):
        self.items: List[ScheduleHistory] = []

    def save(self, history: ScheduleHistory) -> None:
        self.items.append(history)

    def find_by_task_id(self, task_id: UUID) -> List[ScheduleHistory]:
        return sorted(
            [h for h in self.items if h.task_id == task_id],
            key=lambda h: h.created_at
        )

    def find_by_caused_by_task_id(self, caused_by_task_id: UUID) -> List[ScheduleHistory]:
        return [h for h in self.items if h.caused_by_task_id == caused_by_task_id]


class _MockUnitOfWork:
    """Mock unit of work for testing."""

    def __init__(self, task_repo, schedule_history_repo):
        self.tasks = task_repo
        self.schedule_history = schedule_history_repo
        self._entered = False

    def __enter__(self):
        self._entered = True
        return self

    def __exit__(self, *args):
        self._entered = False

    def commit(self):
        pass

    def rollback(self):
        pass


def _make_task(
    task_id: UUID = None,
    title: str = "Test Task",
    is_delayed: bool = False,
    expected_end_offset: int = 0,
    actual_end_offset: int = 0,
) -> Task:
    """Create a task for testing."""
    now = datetime.now(UTC)
    task_id = task_id or uuid4()
    return Task(
        id=task_id,
        project_id=uuid4(),
        title=title,
        description="Test description",
        role_responsible_id=uuid4(),
        status=TaskStatus.DONE if is_delayed else TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        rank_index=1.0,
        expected_start_date=now - timedelta(days=5),
        expected_end_date=now + timedelta(days=expected_end_offset),
        actual_start_date=now - timedelta(days=5) if is_delayed else None,
        actual_end_date=now + timedelta(days=actual_end_offset) if is_delayed else None,
        is_delayed=is_delayed,
    )


class TestGetDelayChainUseCase:
    """Tests for GetDelayChainUseCase (UC-030)."""

    def test_get_delay_chain_task_not_found(self):
        """Should raise BusinessRuleViolation when task not found."""
        task_repo = _InMemoryTaskRepo()
        history_repo = _InMemoryScheduleHistoryRepo()
        uow = _MockUnitOfWork(task_repo, history_repo)

        use_case = GetDelayChainUseCase(uow=uow)

        with pytest.raises(BusinessRuleViolation) as exc_info:
            use_case.execute(uuid4())

        assert exc_info.value.code == "task_not_found"

    def test_get_delay_chain_empty_history(self):
        """Should return empty entries when no schedule history exists."""
        task_repo = _InMemoryTaskRepo()
        history_repo = _InMemoryScheduleHistoryRepo()
        uow = _MockUnitOfWork(task_repo, history_repo)

        task = _make_task(title="Task A")
        task_repo.save(task)

        use_case = GetDelayChainUseCase(uow=uow)
        result = use_case.execute(task.id)

        assert result.task_id == task.id
        assert result.task_title == "Task A"
        assert result.is_delayed is False
        assert result.total_delay_days is None
        assert len(result.entries) == 0
        assert result.root_cause_task_id is None

    def test_get_delay_chain_single_entry(self):
        """Should return single entry when task has one schedule change."""
        task_repo = _InMemoryTaskRepo()
        history_repo = _InMemoryScheduleHistoryRepo()
        uow = _MockUnitOfWork(task_repo, history_repo)

        now = datetime.now(UTC)
        task = _make_task(title="Task B", is_delayed=True, expected_end_offset=0, actual_end_offset=2)
        task_repo.save(task)

        # Create a schedule history entry
        history = ScheduleHistory.create(
            task_id=task.id,
            old_expected_start=now - timedelta(days=5),
            old_expected_end=now,
            new_expected_start=now - timedelta(days=3),
            new_expected_end=now + timedelta(days=2),
            reason=ScheduleChangeReason.MANUAL_OVERRIDE,
            changed_by_user_id=uuid4(),
        )
        history_repo.save(history)

        use_case = GetDelayChainUseCase(uow=uow)
        result = use_case.execute(task.id)

        assert result.task_id == task.id
        assert result.is_delayed is True
        assert result.total_delay_days == pytest.approx(2.0, abs=0.1)
        assert len(result.entries) == 1
        assert result.entries[0].reason == ScheduleChangeReason.MANUAL_OVERRIDE

    def test_get_delay_chain_with_causal_chain(self):
        """Should reconstruct causal chain when delays propagate through dependencies."""
        task_repo = _InMemoryTaskRepo()
        history_repo = _InMemoryScheduleHistoryRepo()
        uow = _MockUnitOfWork(task_repo, history_repo)

        now = datetime.now(UTC)

        # Create a chain: A -> B -> C -> D
        # A is the root cause that delayed everything
        task_a = _make_task(title="Task A", is_delayed=True, expected_end_offset=0, actual_end_offset=3)
        task_b = _make_task(title="Task B", is_delayed=False)
        task_c = _make_task(title="Task C", is_delayed=False)
        task_d = _make_task(title="Task D", is_delayed=False)

        task_repo.save(task_a)
        task_repo.save(task_b)
        task_repo.save(task_c)
        task_repo.save(task_d)

        # Create history entries showing the cascade
        # D was shifted because of C
        history_d = ScheduleHistory.create(
            task_id=task_d.id,
            old_expected_start=now,
            old_expected_end=now + timedelta(days=5),
            new_expected_start=now + timedelta(days=3),
            new_expected_end=now + timedelta(days=8),
            reason=ScheduleChangeReason.DEPENDENCY_DELAY,
            caused_by_task_id=task_c.id,
        )
        history_repo.save(history_d)

        # C was shifted because of B
        history_c = ScheduleHistory.create(
            task_id=task_c.id,
            old_expected_start=now,
            old_expected_end=now + timedelta(days=3),
            new_expected_start=now + timedelta(days=3),
            new_expected_end=now + timedelta(days=6),
            reason=ScheduleChangeReason.DEPENDENCY_DELAY,
            caused_by_task_id=task_b.id,
        )
        history_repo.save(history_c)

        # B was shifted because of A
        history_b = ScheduleHistory.create(
            task_id=task_b.id,
            old_expected_start=now,
            old_expected_end=now + timedelta(days=2),
            new_expected_start=now + timedelta(days=3),
            new_expected_end=now + timedelta(days=5),
            reason=ScheduleChangeReason.DEPENDENCY_DELAY,
            caused_by_task_id=task_a.id,
        )
        history_repo.save(history_b)

        use_case = GetDelayChainUseCase(uow=uow)
        result = use_case.execute(task_d.id)

        assert result.task_id == task_d.id
        assert len(result.entries) == 1
        assert result.entries[0].caused_by_task_id == task_c.id
        assert result.entries[0].caused_by_task_title == "Task C"

    def test_get_delay_chain_multiple_history_entries(self):
        """Should return all history entries in chronological order."""
        task_repo = _InMemoryTaskRepo()
        history_repo = _InMemoryScheduleHistoryRepo()
        uow = _MockUnitOfWork(task_repo, history_repo)

        now = datetime.now(UTC)
        task = _make_task(title="Task with multiple changes")
        task_repo.save(task)

        # First change (earlier)
        history1 = ScheduleHistory(
            id=uuid4(),
            task_id=task.id,
            old_expected_start=now,
            old_expected_end=now + timedelta(days=5),
            new_expected_start=now + timedelta(days=1),
            new_expected_end=now + timedelta(days=6),
            reason=ScheduleChangeReason.ESTIMATION_ERROR,
            caused_by_task_id=None,
            changed_by_user_id=uuid4(),
            created_at=now - timedelta(hours=2),
        )
        history_repo.save(history1)

        # Second change (later)
        history2 = ScheduleHistory(
            id=uuid4(),
            task_id=task.id,
            old_expected_start=now + timedelta(days=1),
            old_expected_end=now + timedelta(days=6),
            new_expected_start=now + timedelta(days=3),
            new_expected_end=now + timedelta(days=8),
            reason=ScheduleChangeReason.SCOPE_CHANGE,
            caused_by_task_id=None,
            changed_by_user_id=uuid4(),
            created_at=now - timedelta(hours=1),
        )
        history_repo.save(history2)

        use_case = GetDelayChainUseCase(uow=uow)
        result = use_case.execute(task.id)

        assert len(result.entries) == 2
        # Should be ordered chronologically
        assert result.entries[0].reason == ScheduleChangeReason.ESTIMATION_ERROR
        assert result.entries[1].reason == ScheduleChangeReason.SCOPE_CHANGE

    def test_get_delay_chain_calculates_total_delay_correctly(self):
        """Should calculate total delay in days from actual vs expected end."""
        task_repo = _InMemoryTaskRepo()
        history_repo = _InMemoryScheduleHistoryRepo()
        uow = _MockUnitOfWork(task_repo, history_repo)

        now = datetime.now(UTC)
        task = Task(
            id=uuid4(),
            project_id=uuid4(),
            title="Delayed Task",
            description="",
            role_responsible_id=uuid4(),
            status=TaskStatus.DONE,
            priority=TaskPriority.MEDIUM,
            rank_index=1.0,
            expected_end_date=now,
            actual_end_date=now + timedelta(days=5, hours=12),  # 5.5 days late
            is_delayed=True,
        )
        task_repo.save(task)

        use_case = GetDelayChainUseCase(uow=uow)
        result = use_case.execute(task.id)

        assert result.is_delayed is True
        assert result.total_delay_days == pytest.approx(5.5, abs=0.01)

    def test_get_delay_chain_handles_missing_caused_by_task(self):
        """Should handle gracefully when caused_by_task no longer exists."""
        task_repo = _InMemoryTaskRepo()
        history_repo = _InMemoryScheduleHistoryRepo()
        uow = _MockUnitOfWork(task_repo, history_repo)

        now = datetime.now(UTC)
        task = _make_task(title="Task X")
        task_repo.save(task)

        # History references a task that doesn't exist
        missing_task_id = uuid4()
        history = ScheduleHistory.create(
            task_id=task.id,
            old_expected_start=now,
            old_expected_end=now + timedelta(days=5),
            new_expected_start=now + timedelta(days=2),
            new_expected_end=now + timedelta(days=7),
            reason=ScheduleChangeReason.DEPENDENCY_DELAY,
            caused_by_task_id=missing_task_id,
        )
        history_repo.save(history)

        use_case = GetDelayChainUseCase(uow=uow)
        result = use_case.execute(task.id)

        # Should not crash, but caused_by_task_title should be None
        assert len(result.entries) == 1
        assert result.entries[0].caused_by_task_id == missing_task_id
        assert result.entries[0].caused_by_task_title is None


class TestDelayChainEdgeCases:
    """Edge case tests for delay chain retrieval."""

    def test_task_not_delayed_but_has_history(self):
        """Task may have schedule history but not be marked as delayed."""
        task_repo = _InMemoryTaskRepo()
        history_repo = _InMemoryScheduleHistoryRepo()
        uow = _MockUnitOfWork(task_repo, history_repo)

        now = datetime.now(UTC)
        # Task finished on time
        task = Task(
            id=uuid4(),
            project_id=uuid4(),
            title="On-time Task",
            description="",
            role_responsible_id=uuid4(),
            status=TaskStatus.DONE,
            priority=TaskPriority.MEDIUM,
            rank_index=1.0,
            expected_end_date=now + timedelta(days=5),
            actual_end_date=now + timedelta(days=3),  # Finished early!
            is_delayed=False,
        )
        task_repo.save(task)

        # But it has history from earlier adjustments
        history = ScheduleHistory.create(
            task_id=task.id,
            old_expected_start=now,
            old_expected_end=now + timedelta(days=3),
            new_expected_start=now,
            new_expected_end=now + timedelta(days=5),
            reason=ScheduleChangeReason.SCOPE_CHANGE,
        )
        history_repo.save(history)

        use_case = GetDelayChainUseCase(uow=uow)
        result = use_case.execute(task.id)

        assert result.is_delayed is False
        assert result.total_delay_days is None  # Not delayed, so no delay to report
        assert len(result.entries) == 1

    def test_circular_reference_in_history_doesnt_loop_forever(self):
        """Should handle potential circular references gracefully."""
        task_repo = _InMemoryTaskRepo()
        history_repo = _InMemoryScheduleHistoryRepo()
        uow = _MockUnitOfWork(task_repo, history_repo)

        now = datetime.now(UTC)
        task_a = _make_task(title="Task A")
        task_b = _make_task(title="Task B")
        task_repo.save(task_a)
        task_repo.save(task_b)

        # Create history that could form a cycle: A caused by B, B caused by A
        # (This shouldn't happen in practice, but we should handle it)
        history_a = ScheduleHistory.create(
            task_id=task_a.id,
            old_expected_start=now,
            old_expected_end=now + timedelta(days=5),
            new_expected_start=now + timedelta(days=1),
            new_expected_end=now + timedelta(days=6),
            reason=ScheduleChangeReason.DEPENDENCY_DELAY,
            caused_by_task_id=task_b.id,
        )
        history_repo.save(history_a)

        history_b = ScheduleHistory.create(
            task_id=task_b.id,
            old_expected_start=now,
            old_expected_end=now + timedelta(days=3),
            new_expected_start=now + timedelta(days=1),
            new_expected_end=now + timedelta(days=4),
            reason=ScheduleChangeReason.DEPENDENCY_DELAY,
            caused_by_task_id=task_a.id,  # Creates potential cycle!
        )
        history_repo.save(history_b)

        use_case = GetDelayChainUseCase(uow=uow)

        # Should complete without infinite loop
        result = use_case.execute(task_a.id)
        assert result.task_id == task_a.id
        assert len(result.entries) == 1

    def test_task_with_null_dates(self):
        """Should handle tasks with null expected/actual dates."""
        task_repo = _InMemoryTaskRepo()
        history_repo = _InMemoryScheduleHistoryRepo()
        uow = _MockUnitOfWork(task_repo, history_repo)

        task = Task(
            id=uuid4(),
            project_id=uuid4(),
            title="Task with null dates",
            description="",
            role_responsible_id=uuid4(),
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            rank_index=1.0,
            expected_start_date=None,
            expected_end_date=None,
            actual_start_date=None,
            actual_end_date=None,
            is_delayed=False,
        )
        task_repo.save(task)

        use_case = GetDelayChainUseCase(uow=uow)
        result = use_case.execute(task.id)

        assert result.is_delayed is False
        assert result.total_delay_days is None
        assert len(result.entries) == 0
