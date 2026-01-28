"""Unit tests for ScheduleService and schedule-related behavior (Spec 2.0)."""
from datetime import datetime, timedelta, UTC
from uuid import uuid4

class _InMemoryTaskRepo:
    def __init__(self):
        self.tasks = {}

    def save(self, task):
        self.tasks[task.id] = task

    def find_by_id(self, task_id):
        return self.tasks.get(task_id)

    def find_dependent_tasks(self, task_id):
        # Simple adjacency: tasks whose project_id equals the blocker id in this test
        return [t for t in self.tasks.values() if getattr(t, "_depends_on", None) == task_id]


class _InMemoryDepRepo:
    def __init__(self):
        self.deps = []


class _InMemoryHistoryRepo:
    def __init__(self):
        self.items = []

    def save(self, history):
        self.items.append(history)

    def find_by_task_id(self, task_id):
        return [h for h in self.items if h.task_id == task_id]


class _InMemoryBus:
    def __init__(self):
        self.events = []

    def subscribe(self, *_args, **_kwargs):
        # Not needed for these unit tests
        return None

    def emit(self, event):
        self.events.append(event)


def _make_task_with_schedule(expected_end_offset_days=0, actual_end_offset_days=0, delayed=False):
    from app.domain.models.task import Task
    from app.domain.models.enums import TaskStatus, TaskPriority

    now = datetime.now(UTC)
    task_id = uuid4()
    expected_end = now + timedelta(days=expected_end_offset_days)
    actual_end = now + timedelta(days=actual_end_offset_days)

    return Task(
        id=task_id,
        project_id=uuid4(),
        title="T",
        description="D",
        role_responsible_id=uuid4(),
        status=TaskStatus.DONE,
        priority=TaskPriority.MEDIUM,
        rank_index=1.0,
        user_responsible_id=None,
        completion_percentage=100,
        completion_source=None,
        due_date=None,
        expected_start_date=now,
        expected_end_date=expected_end,
        actual_start_date=now,
        actual_end_date=actual_end,
        is_delayed=delayed,
    )


def test_detect_delay_marks_task_and_emits_event():
    """BR-023 / UC-027: task is marked delayed when actual_end > expected_end."""
    from app.application.services.schedule_service import ScheduleService

    task_repo = _InMemoryTaskRepo()
    dep_repo = _InMemoryDepRepo()
    history_repo = _InMemoryHistoryRepo()
    bus = _InMemoryBus()

    service = ScheduleService(
        task_repository=task_repo,
        task_dependency_repository=dep_repo,
        schedule_history_repository=history_repo,
        event_bus=bus,
    )

    task = _make_task_with_schedule(expected_end_offset_days=0, actual_end_offset_days=1)
    task_repo.save(task)

    delayed = service.detect_delay(task)

    assert delayed is True
    assert task.is_delayed is True
    assert any(e.__class__.__name__ == "TaskDelayed" for e in bus.events)


def test_detect_delay_no_delay_when_actual_before_expected():
    """No delay when actual_end <= expected_end."""
    from app.application.services.schedule_service import ScheduleService

    task_repo = _InMemoryTaskRepo()
    dep_repo = _InMemoryDepRepo()
    history_repo = _InMemoryHistoryRepo()
    bus = _InMemoryBus()

    service = ScheduleService(
        task_repository=task_repo,
        task_dependency_repository=dep_repo,
        schedule_history_repository=history_repo,
        event_bus=bus,
    )

    task = _make_task_with_schedule(expected_end_offset_days=1, actual_end_offset_days=0)
    task_repo.save(task)

    delayed = service.detect_delay(task)

    assert delayed is False
    assert task.is_delayed is False
    assert not any(e.__class__.__name__ == "TaskDelayed" for e in bus.events)


def test_propagate_delay_shifts_dependents_and_creates_history():
    """UC-028: delay on root task shifts dependents and records ScheduleHistory."""
    from app.application.services.schedule_service import ScheduleService
    from app.domain.models.task import Task
    from app.domain.models.enums import TaskStatus, TaskPriority

    task_repo = _InMemoryTaskRepo()
    dep_repo = _InMemoryDepRepo()
    history_repo = _InMemoryHistoryRepo()
    bus = _InMemoryBus()

    service = ScheduleService(
        task_repository=task_repo,
        task_dependency_repository=dep_repo,
        schedule_history_repository=history_repo,
        event_bus=bus,
    )

    now = datetime.now(UTC)

    # Root task delayed by +2 days
    root = Task(
        id=uuid4(),
        project_id=uuid4(),
        title="Root",
        description="",
        role_responsible_id=uuid4(),
        status=TaskStatus.DONE,
        priority=TaskPriority.MEDIUM,
        rank_index=1.0,
        user_responsible_id=None,
        completion_percentage=100,
        completion_source=None,
        due_date=None,
        expected_start_date=now,
        expected_end_date=now,
        actual_start_date=now,
        actual_end_date=now + timedelta(days=2),
        is_delayed=True,
    )

    dep = Task(
        id=uuid4(),
        project_id=uuid4(),
        title="Child",
        description="",
        role_responsible_id=uuid4(),
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        rank_index=1.0,
        user_responsible_id=None,
        completion_percentage=None,
        completion_source=None,
        due_date=None,
        expected_start_date=now + timedelta(days=1),
        expected_end_date=now + timedelta(days=3),
        actual_start_date=None,
        actual_end_date=None,
        is_delayed=False,
    )
    # mark dependency in in-memory repo
    dep._depends_on = root.id  # type: ignore[attr-defined]

    task_repo.save(root)
    task_repo.save(dep)

    service.propagate_delay(root)

    # Dependent task should be shifted by +2 days
    assert dep.expected_start_date == now + timedelta(days=3)
    assert dep.expected_end_date == now + timedelta(days=5)

    # History should be created for dependent
    dep_history = history_repo.find_by_task_id(dep.id)
    assert len(dep_history) == 1
    assert dep_history[0].old_expected_start == now + timedelta(days=1)
    assert dep_history[0].new_expected_start == now + timedelta(days=3)

    # ScheduleChanged event emitted
    assert any(e.__class__.__name__ == "ScheduleChanged" for e in bus.events)

