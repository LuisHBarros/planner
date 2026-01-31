"""Dependency validation per BR-DEP."""
from typing import Dict, List, Set

from app.domain.models.value_objects import TaskId


def detect_cycle(
    task_id: TaskId,
    depends_on_id: TaskId,
    existing_dependencies: Dict[TaskId, List[TaskId]],  # task_id -> [depends_on_ids]
) -> bool:
    """
    Detect if adding dependency would create a cycle (BR-DEP-002).

    Uses DFS to check if depends_on_id can reach task_id.
    """
    if task_id == depends_on_id:
        return True  # Self-dependency

    visited: Set[TaskId] = set()
    stack: List[TaskId] = [depends_on_id]

    while stack:
        current = stack.pop()
        if current == task_id:
            return True  # Found cycle

        if current in visited:
            continue
        visited.add(current)

        # Add dependencies of current task
        for dep_id in existing_dependencies.get(current, []):
            stack.append(dep_id)

    return False
