"""Unit tests for RemoveTaskDependencyUseCase."""
from datetime import datetime, UTC
from uuid import uuid4

import pytest

from app.application.use_cases.remove_task_dependency import RemoveTaskDependencyUseCase
from app.domain.models.task import Task
from app.domain.models.task_dependency import TaskDependency
from app.domain.models.project import Project
from app.domain.models.enums import TaskStatus, TaskPriority, DependencyType
from app.domain.exceptions import BusinessRuleViolation


class _InMemoryTaskRepo:
    def __init__(self):
        self.tasks = {}

    def save(self, task):
        self.tasks[task.id] = task

    def find_by_id(self, task_id):
        return self.tasks.get(task_id)


class _InMemoryDepRepo:
    def __init__(self):
        self.deps = {}

    def save(self, dep):
        self.deps[dep.id] = dep

    def find_by_id(self, dep_id):
        return self.deps.get(dep_id)

    def find_by_task_id(self, task_id):
        return [d for d in self.deps.values() if d.task_id == task_id]

    def delete(self, dep_id):
        if dep_id in self.deps:
            del self.deps[dep_id]


class _InMemoryProjectRepo:
    def __init__(self):
        self.projects = {}

    def save(self, project):
        self.projects[project.id] = project

    def find_by_id(self, project_id):
        return self.projects.get(project_id)


class _InMemoryNoteRepo:
    def __init__(self):
        self.notes = []

    def save(self, note):
        self.notes.append(note)


class _InMemoryBus:
    def __init__(self):
        self.events = []

    def emit(self, event):
        self.events.append(event)


def test_remove_dependency_success():
    """Removing a dependency deletes it and creates a note."""
    task_repo = _InMemoryTaskRepo()
    dep_repo = _InMemoryDepRepo()
    project_repo = _InMemoryProjectRepo()
    note_repo = _InMemoryNoteRepo()
    bus = _InMemoryBus()

    project = Project.create(team_id=uuid4(), name="P")
    project_repo.save(project)

    task = Task.create(
        project_id=project.id,
        title="T",
        description="D",
        role_responsible_id=uuid4(),
    )
    task_repo.save(task)

    dep = TaskDependency.create(
        task_id=task.id,
        depends_on_task_id=uuid4(),
        dependency_type=DependencyType.RELATES_TO,
    )
    dep_repo.save(dep)

    use_case = RemoveTaskDependencyUseCase(
        task_repository=task_repo,
        task_dependency_repository=dep_repo,
        project_repository=project_repo,
        note_repository=note_repo,
        team_member_repository=None,
        event_bus=bus,
    )

    use_case.execute(task_id=task.id, dependency_id=dep.id)

    assert dep.id not in dep_repo.deps
    assert len(note_repo.notes) == 1


def test_remove_blocking_dependency_unblocks_task():
    """Removing last blocking dependency unblocks task."""
    task_repo = _InMemoryTaskRepo()
    dep_repo = _InMemoryDepRepo()
    project_repo = _InMemoryProjectRepo()
    note_repo = _InMemoryNoteRepo()
    bus = _InMemoryBus()

    project = Project.create(team_id=uuid4(), name="P")
    project_repo.save(project)

    blocker = Task.create(
        project_id=project.id,
        title="Blocker",
        description="",
        role_responsible_id=uuid4(),
    )
    blocker.status = TaskStatus.DONE
    task_repo.save(blocker)

    task = Task.create(
        project_id=project.id,
        title="T",
        description="D",
        role_responsible_id=uuid4(),
    )
    task.status = TaskStatus.BLOCKED
    task_repo.save(task)

    dep = TaskDependency.create(
        task_id=task.id,
        depends_on_task_id=blocker.id,
        dependency_type=DependencyType.BLOCKS,
    )
    dep_repo.save(dep)

    use_case = RemoveTaskDependencyUseCase(
        task_repository=task_repo,
        task_dependency_repository=dep_repo,
        project_repository=project_repo,
        note_repository=note_repo,
        team_member_repository=None,
        event_bus=bus,
    )

    use_case.execute(task_id=task.id, dependency_id=dep.id)

    updated_task = task_repo.find_by_id(task.id)
    assert updated_task.status == TaskStatus.TODO
    assert updated_task.blocked_reason is None
    assert any(e.__class__.__name__ == "TaskUnblocked" for e in bus.events)


def test_remove_blocking_dependency_does_not_unblock_if_other_blockers_exist():
    """Task stays blocked if other blocking dependencies remain."""
    task_repo = _InMemoryTaskRepo()
    dep_repo = _InMemoryDepRepo()
    project_repo = _InMemoryProjectRepo()
    note_repo = _InMemoryNoteRepo()
    bus = _InMemoryBus()

    project = Project.create(team_id=uuid4(), name="P")
    project_repo.save(project)

    blocker1 = Task.create(
        project_id=project.id,
        title="B1",
        description="",
        role_responsible_id=uuid4(),
    )
    blocker1.status = TaskStatus.DONE
    task_repo.save(blocker1)

    blocker2 = Task.create(
        project_id=project.id,
        title="B2",
        description="",
        role_responsible_id=uuid4(),
    )
    blocker2.status = TaskStatus.DOING
    task_repo.save(blocker2)

    task = Task.create(
        project_id=project.id,
        title="T",
        description="D",
        role_responsible_id=uuid4(),
    )
    task.status = TaskStatus.BLOCKED
    task_repo.save(task)

    dep1 = TaskDependency.create(
        task_id=task.id,
        depends_on_task_id=blocker1.id,
        dependency_type=DependencyType.BLOCKS,
    )
    dep_repo.save(dep1)

    dep2 = TaskDependency.create(
        task_id=task.id,
        depends_on_task_id=blocker2.id,
        dependency_type=DependencyType.BLOCKS,
    )
    dep_repo.save(dep2)

    use_case = RemoveTaskDependencyUseCase(
        task_repository=task_repo,
        task_dependency_repository=dep_repo,
        project_repository=project_repo,
        note_repository=note_repo,
        team_member_repository=None,
        event_bus=bus,
    )

    use_case.execute(task_id=task.id, dependency_id=dep1.id)

    updated_task = task_repo.find_by_id(task.id)
    assert updated_task.status == TaskStatus.BLOCKED
    assert not any(e.__class__.__name__ == "TaskUnblocked" for e in bus.events)


def test_remove_dependency_does_not_change_doing_or_done_status():
    """Removing dependency does not change status if task is doing or done."""
    task_repo = _InMemoryTaskRepo()
    dep_repo = _InMemoryDepRepo()
    project_repo = _InMemoryProjectRepo()
    note_repo = _InMemoryNoteRepo()
    bus = _InMemoryBus()

    project = Project.create(team_id=uuid4(), name="P")
    project_repo.save(project)

    blocker = Task.create(
        project_id=project.id,
        title="B",
        description="",
        role_responsible_id=uuid4(),
    )
    blocker.status = TaskStatus.DONE
    task_repo.save(blocker)

    task = Task.create(
        project_id=project.id,
        title="T",
        description="D",
        role_responsible_id=uuid4(),
    )
    task.status = TaskStatus.DOING
    task_repo.save(task)

    dep = TaskDependency.create(
        task_id=task.id,
        depends_on_task_id=blocker.id,
        dependency_type=DependencyType.BLOCKS,
    )
    dep_repo.save(dep)

    use_case = RemoveTaskDependencyUseCase(
        task_repository=task_repo,
        task_dependency_repository=dep_repo,
        project_repository=project_repo,
        note_repository=note_repo,
        team_member_repository=None,
        event_bus=bus,
    )

    use_case.execute(task_id=task.id, dependency_id=dep.id)

    updated_task = task_repo.find_by_id(task.id)
    assert updated_task.status == TaskStatus.DOING


def test_remove_dependency_not_found():
    """Removing non-existent dependency raises dependency_not_found."""
    task_repo = _InMemoryTaskRepo()
    dep_repo = _InMemoryDepRepo()
    project_repo = _InMemoryProjectRepo()
    note_repo = _InMemoryNoteRepo()

    project = Project.create(team_id=uuid4(), name="P")
    project_repo.save(project)

    task = Task.create(
        project_id=project.id,
        title="T",
        description="D",
        role_responsible_id=uuid4(),
    )
    task_repo.save(task)

    use_case = RemoveTaskDependencyUseCase(
        task_repository=task_repo,
        task_dependency_repository=dep_repo,
        project_repository=project_repo,
        note_repository=note_repo,
        team_member_repository=None,
        event_bus=None,
    )

    with pytest.raises(BusinessRuleViolation) as exc_info:
        use_case.execute(task_id=task.id, dependency_id=uuid4())

    assert exc_info.value.code == "dependency_not_found"


def test_remove_dependency_mismatch():
    """Removing dependency that belongs to different task raises dependency_mismatch."""
    task_repo = _InMemoryTaskRepo()
    dep_repo = _InMemoryDepRepo()
    project_repo = _InMemoryProjectRepo()
    note_repo = _InMemoryNoteRepo()

    project = Project.create(team_id=uuid4(), name="P")
    project_repo.save(project)

    task1 = Task.create(
        project_id=project.id,
        title="T1",
        description="D",
        role_responsible_id=uuid4(),
    )
    task_repo.save(task1)

    task2 = Task.create(
        project_id=project.id,
        title="T2",
        description="D",
        role_responsible_id=uuid4(),
    )
    task_repo.save(task2)

    dep = TaskDependency.create(
        task_id=task1.id,
        depends_on_task_id=uuid4(),
        dependency_type=DependencyType.BLOCKS,
    )
    dep_repo.save(dep)

    use_case = RemoveTaskDependencyUseCase(
        task_repository=task_repo,
        task_dependency_repository=dep_repo,
        project_repository=project_repo,
        note_repository=note_repo,
        team_member_repository=None,
        event_bus=None,
    )

    with pytest.raises(BusinessRuleViolation) as exc_info:
        use_case.execute(task_id=task2.id, dependency_id=dep.id)

    assert exc_info.value.code == "dependency_mismatch"
