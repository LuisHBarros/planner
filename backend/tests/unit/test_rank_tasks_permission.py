"""Unit tests for RankTasksUseCase permission enforcement."""
from uuid import uuid4

import pytest

from app.application.use_cases.rank_tasks import RankTasksUseCase
from app.domain.models.task import Task
from app.domain.models.project import Project
from app.domain.models.enums import TaskStatus, TaskPriority
from app.domain.exceptions import BusinessRuleViolation

try:
    from app.domain.models.team_member import TeamMember
    from app.domain.models.enums import TeamMemberRole
except ImportError:
    TeamMember = None
    TeamMemberRole = None


class _InMemoryTaskRepo:
    def __init__(self):
        self.tasks = {}

    def save(self, task):
        self.tasks[task.id] = task

    def find_by_project_id(self, project_id):
        return [t for t in self.tasks.values() if t.project_id == project_id]


class _InMemoryProjectRepo:
    def __init__(self):
        self.projects = {}

    def find_by_id(self, project_id):
        return self.projects.get(project_id)


class _InMemoryMemberRepo:
    def __init__(self):
        self.members = {}

    def find_by_user_id(self, user_id):
        return [m for m in self.members.values() if m.user_id == user_id]


class _InMemoryBus:
    def __init__(self):
        self.events = []

    def emit(self, event):
        self.events.append(event)


def test_rank_tasks_without_permission_check_mvp():
    """RankTasks works without permission check when team_member_repo is None (MVP)."""
    task_repo = _InMemoryTaskRepo()
    project_repo = _InMemoryProjectRepo()
    bus = _InMemoryBus()

    project = Project.create(team_id=uuid4(), name="P")
    project_repo.projects[project.id] = project

    task1 = Task.create(
        project_id=project.id,
        title="T1",
        description="",
        role_responsible_id=uuid4(),
    )
    task2 = Task.create(
        project_id=project.id,
        title="T2",
        description="",
        role_responsible_id=uuid4(),
    )
    task_repo.tasks[task1.id] = task1
    task_repo.tasks[task2.id] = task2

    use_case = RankTasksUseCase(
        task_repository=task_repo,
        project_repository=project_repo,
        event_bus=bus,
        team_member_repository=None,
    )

    tasks = use_case.execute(
        project_id=project.id,
        task_ids=[task2.id, task1.id],
        actor_user_id=None,
    )

    assert len(tasks) == 2
    assert tasks[0].id == task2.id
    assert tasks[1].id == task1.id


def test_rank_tasks_with_manager_permission():
    """RankTasks succeeds when actor is manager."""
    if TeamMember is None or TeamMemberRole is None:
        pytest.skip("TeamMember not available")

    task_repo = _InMemoryTaskRepo()
    project_repo = _InMemoryProjectRepo()
    member_repo = _InMemoryMemberRepo()
    bus = _InMemoryBus()

    team_id = uuid4()
    project = Project.create(team_id=team_id, name="P")
    project_repo.projects[project.id] = project

    manager_id = uuid4()
    member = TeamMember.join(
        user_id=manager_id,
        team_id=team_id,
        role=TeamMemberRole.MANAGER,
    )
    member_repo.members[member.id] = member

    task1 = Task.create(
        project_id=project.id,
        title="T1",
        description="",
        role_responsible_id=uuid4(),
    )
    task_repo.tasks[task1.id] = task1

    use_case = RankTasksUseCase(
        task_repository=task_repo,
        project_repository=project_repo,
        event_bus=bus,
        team_member_repository=member_repo,
    )

    tasks = use_case.execute(
        project_id=project.id,
        task_ids=[task1.id],
        actor_user_id=manager_id,
    )

    assert len(tasks) == 1


def test_rank_tasks_denies_non_manager():
    """RankTasks raises permission_denied when actor is not manager."""
    if TeamMember is None or TeamMemberRole is None:
        pytest.skip("TeamMember not available")

    task_repo = _InMemoryTaskRepo()
    project_repo = _InMemoryProjectRepo()
    member_repo = _InMemoryMemberRepo()
    bus = _InMemoryBus()

    team_id = uuid4()
    project = Project.create(team_id=team_id, name="P")
    project_repo.projects[project.id] = project

    member_id = uuid4()
    member = TeamMember.join(
        user_id=member_id,
        team_id=team_id,
        role=TeamMemberRole.MEMBER,
    )
    member_repo.members[member.id] = member

    task1 = Task.create(
        project_id=project.id,
        title="T1",
        description="",
        role_responsible_id=uuid4(),
    )
    task_repo.tasks[task1.id] = task1

    use_case = RankTasksUseCase(
        task_repository=task_repo,
        project_repository=project_repo,
        event_bus=bus,
        team_member_repository=member_repo,
    )

    with pytest.raises(BusinessRuleViolation) as exc_info:
        use_case.execute(
            project_id=project.id,
            task_ids=[task1.id],
            actor_user_id=member_id,
        )

    assert exc_info.value.code == "permission_denied"
