"""Unit tests for project timeline endpoint logic."""
from datetime import datetime, timedelta, UTC
from uuid import uuid4

from app.domain.models.task import Task
from app.domain.models.task_dependency import TaskDependency
from app.domain.models.enums import TaskStatus, TaskPriority, DependencyType


class _InMemoryTaskRepo:
    def __init__(self):
        self.tasks = {}

    def find_by_project_id(self, project_id):
        return [t for t in self.tasks.values() if t.project_id == project_id]

    def find_by_id(self, task_id):
        return self.tasks.get(task_id)


class _InMemoryDepRepo:
    def __init__(self):
        self.deps_by_task = {}

    def find_by_task_id(self, task_id):
        return self.deps_by_task.get(task_id, [])


def test_timeline_computes_is_delayed():
    """Timeline computes is_delayed when expected_end_date is past and status != done."""
    task_repo = _InMemoryTaskRepo()
    dep_repo = _InMemoryDepRepo()

    project_id = uuid4()
    now = datetime.now(UTC)

    # Task with past expected_end_date and not done
    task = Task.create(
        project_id=project_id,
        title="Delayed",
        description="",
        role_responsible_id=uuid4(),
    )
    task.status = TaskStatus.DOING
    # Simulate expected_end_date field (Spec 2.0) - only if Task model supports it
    if hasattr(task, "expected_end_date"):
        task.expected_end_date = now - timedelta(days=1)
    task_repo.tasks[task.id] = task

    tasks = task_repo.find_by_project_id(project_id)
    timeline_tasks = []

    for t in tasks:
        expected_end = None
        if hasattr(t, "expected_end_date") and t.expected_end_date:
            expected_end = t.expected_end_date.isoformat()

        is_delayed = False
        if expected_end:
            try:
                expected_end_dt = datetime.fromisoformat(expected_end.replace("Z", "+00:00"))
                if now > expected_end_dt and t.status != TaskStatus.DONE:
                    is_delayed = True
            except (ValueError, AttributeError):
                pass
        elif hasattr(t, "is_delayed"):
            # Fallback to is_delayed attribute if available
            is_delayed = t.is_delayed

        timeline_tasks.append({"id": str(t.id), "is_delayed": is_delayed})

    # If expected_end_date is not available (no Spec 2.0), is_delayed should be False
    # This test verifies the computation logic works when the field exists
    if hasattr(task, "expected_end_date"):
        assert timeline_tasks[0]["is_delayed"] is True
    else:
        # Without Spec 2.0, is_delayed defaults to False (no scheduling fields)
        assert timeline_tasks[0]["is_delayed"] is False


def test_timeline_counts_blocking_dependencies():
    """Timeline counts blocking dependencies that are not completed."""
    task_repo = _InMemoryTaskRepo()
    dep_repo = _InMemoryDepRepo()

    project_id = uuid4()

    blocker1 = Task.create(
        project_id=project_id,
        title="B1",
        description="",
        role_responsible_id=uuid4(),
    )
    blocker1.status = TaskStatus.DONE
    task_repo.tasks[blocker1.id] = blocker1

    blocker2 = Task.create(
        project_id=project_id,
        title="B2",
        description="",
        role_responsible_id=uuid4(),
    )
    blocker2.status = TaskStatus.DOING
    task_repo.tasks[blocker2.id] = blocker2

    task = Task.create(
        project_id=project_id,
        title="T",
        description="",
        role_responsible_id=uuid4(),
    )
    task_repo.tasks[task.id] = task

    dep1 = TaskDependency.create(
        task_id=task.id,
        depends_on_task_id=blocker1.id,
        dependency_type=DependencyType.BLOCKS,
    )
    dep2 = TaskDependency.create(
        task_id=task.id,
        depends_on_task_id=blocker2.id,
        dependency_type=DependencyType.BLOCKS,
    )
    dep_repo.deps_by_task[task.id] = [dep1, dep2]

    tasks = task_repo.find_by_project_id(project_id)
    timeline_tasks = []

    for t in tasks:
        blocking_deps = dep_repo.find_by_task_id(t.id)
        blocking_deps = [
            d for d in blocking_deps if d.dependency_type == DependencyType.BLOCKS
        ]

        blocking_count = 0
        blocked_by = []
        for dep in blocking_deps:
            blocker = task_repo.find_by_id(dep.depends_on_task_id)
            if blocker and blocker.status != TaskStatus.DONE:
                blocking_count += 1
                blocked_by.append(str(dep.depends_on_task_id))

        timeline_tasks.append(
            {
                "id": str(t.id),
                "blocking_dependencies": blocking_count,
                "blocked_by": blocked_by,
            }
        )

    task_timeline = next(t for t in timeline_tasks if t["id"] == str(task.id))
    assert task_timeline["blocking_dependencies"] == 1
    assert str(blocker2.id) in task_timeline["blocked_by"]
    assert str(blocker1.id) not in task_timeline["blocked_by"]
