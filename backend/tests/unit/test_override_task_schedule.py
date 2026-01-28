"""Unit tests for OverrideTaskScheduleUseCase (UC-029)."""
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
        # For this test we don't assert propagation, so return empty
        return []


class _InMemoryHistoryRepo:
    def __init__(self):
        self.items = []

    def save(self, history):
        self.items.append(history)

    def find_by_task_id(self, task_id):
        return [h for h in self.items if h.task_id == task_id]


class _InMemoryDepRepo:
    def __init__(self):
        self.deps = []


class _InMemoryBus:
    def __init__(self):
        self.events = []

    def subscribe(self, *_args, **_kwargs):
        return None

    def emit(self, event):
        self.events.append(event)


def test_override_task_schedule_creates_history_and_event():
    """UC-029: manual schedule override persists and is audited."""
    from app.application.use_cases.override_task_schedule import OverrideTaskScheduleUseCase
    from app.domain.models.task import Task
    from app.domain.models.enums import TaskStatus, TaskPriority, ScheduleChangeReason

    task_repo = _InMemoryTaskRepo()
    history_repo = _InMemoryHistoryRepo()
    dep_repo = _InMemoryDepRepo()
    bus = _InMemoryBus()

    use_case = OverrideTaskScheduleUseCase(
        task_repository=task_repo,
        schedule_history_repository=history_repo,
        task_dependency_repository=dep_repo,
        event_bus=bus,
    )

    now = datetime.now(UTC)
    task = Task(
        id=uuid4(),
        project_id=uuid4(),
        title="Test",
        description="",
        role_responsible_id=uuid4(),
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        rank_index=1.0,
        user_responsible_id=None,
        completion_percentage=None,
        completion_source=None,
        due_date=None,
        expected_start_date=now,
        expected_end_date=now + timedelta(days=3),
        actual_start_date=None,
        actual_end_date=None,
        is_delayed=False,
    )
    task_repo.save(task)

    manager_id = uuid4()
    new_start = now + timedelta(days=1)
    new_end = now + timedelta(days=4)

    updated = use_case.execute(
        task_id=task.id,
        new_expected_start=new_start,
        new_expected_end=new_end,
        reason=ScheduleChangeReason.MANUAL_OVERRIDE,
        changed_by_user_id=manager_id,
    )

    # Task fields updated
    assert updated.expected_start_date == new_start
    assert updated.expected_end_date == new_end

    # History recorded
    history_items = history_repo.find_by_task_id(task.id)
    assert len(history_items) == 1
    entry = history_items[0]
    assert entry.old_expected_start == now
    assert entry.old_expected_end == now + timedelta(days=3)
    assert entry.new_expected_start == new_start
    assert entry.new_expected_end == new_end
    assert entry.reason == ScheduleChangeReason.MANUAL_OVERRIDE
    assert entry.changed_by_user_id == manager_id

    # Event emitted
    assert any(e.__class__.__name__ == "ScheduleOverridden" for e in bus.events)

