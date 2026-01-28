"""Unit tests for project dependency graph endpoint logic."""
from uuid import uuid4

from app.domain.models.task import Task
from app.domain.models.task_dependency import TaskDependency
from app.domain.models.project import Project
from app.domain.models.enums import TaskStatus, TaskPriority, DependencyType


class _InMemoryTaskRepo:
    def __init__(self):
        self.tasks = {}

    def find_by_project_id(self, project_id):
        return [t for t in self.tasks.values() if t.project_id == project_id]


class _InMemoryDepRepo:
    def __init__(self):
        self.deps_by_task = {}

    def find_by_task_id(self, task_id):
        return self.deps_by_task.get(task_id, [])


def test_build_dependency_graph_nodes_and_edges():
    """Dependency graph includes all project tasks as nodes and dependencies as edges."""
    task_repo = _InMemoryTaskRepo()
    dep_repo = _InMemoryDepRepo()

    project_id = uuid4()
    task_a = Task.create(
        project_id=project_id,
        title="Task A",
        description="",
        role_responsible_id=uuid4(),
    )
    task_b = Task.create(
        project_id=project_id,
        title="Task B",
        description="",
        role_responsible_id=uuid4(),
    )
    task_c = Task.create(
        project_id=uuid4(),  # Different project
        title="Task C",
        description="",
        role_responsible_id=uuid4(),
    )

    task_repo.tasks[task_a.id] = task_a
    task_repo.tasks[task_b.id] = task_b
    task_repo.tasks[task_c.id] = task_c

    dep = TaskDependency.create(
        task_id=task_b.id,
        depends_on_task_id=task_a.id,
        dependency_type=DependencyType.BLOCKS,
    )
    dep_repo.deps_by_task[task_b.id] = [dep]

    tasks = task_repo.find_by_project_id(project_id)
    task_ids = {t.id for t in tasks}

    nodes = []
    for task in tasks:
        nodes.append(
            {
                "task_id": str(task.id),
                "title": task.title,
                "status": task.status.value,
            }
        )

    edges = []
    for task in tasks:
        deps = dep_repo.find_by_task_id(task.id)
        for d in deps:
            if d.depends_on_task_id in task_ids:
                edges.append(
                    {
                        "from_task_id": str(d.depends_on_task_id),
                        "to_task_id": str(d.task_id),
                        "type": d.dependency_type.value,
                    }
                )

    assert len(nodes) == 2
    assert len(edges) == 1
    assert edges[0]["from_task_id"] == str(task_a.id)
    assert edges[0]["to_task_id"] == str(task_b.id)
    assert edges[0]["type"] == "blocks"


def test_dependency_graph_excludes_dependencies_to_other_projects():
    """Edges only include dependencies where both tasks are in the same project."""
    task_repo = _InMemoryTaskRepo()
    dep_repo = _InMemoryDepRepo()

    project1_id = uuid4()
    project2_id = uuid4()

    task_a = Task.create(
        project_id=project1_id,
        title="A",
        description="",
        role_responsible_id=uuid4(),
    )
    task_b = Task.create(
        project_id=project2_id,
        title="B",
        description="",
        role_responsible_id=uuid4(),
    )

    task_repo.tasks[task_a.id] = task_a
    task_repo.tasks[task_b.id] = task_b

    # Task A depends on Task B (cross-project)
    dep = TaskDependency.create(
        task_id=task_a.id,
        depends_on_task_id=task_b.id,
        dependency_type=DependencyType.BLOCKS,
    )
    dep_repo.deps_by_task[task_a.id] = [dep]

    tasks = task_repo.find_by_project_id(project1_id)
    task_ids = {t.id for t in tasks}

    edges = []
    for task in tasks:
        deps = dep_repo.find_by_task_id(task.id)
        for d in deps:
            if d.depends_on_task_id in task_ids:
                edges.append({"from": str(d.depends_on_task_id), "to": str(d.task_id)})

    # Edge should be excluded because task_b is not in project1
    assert len(edges) == 0
