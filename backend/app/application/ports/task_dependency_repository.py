"""Task dependency repository port."""
from typing import Protocol, Optional, List
from uuid import UUID
from app.domain.models.task_dependency import TaskDependency


class TaskDependencyRepository(Protocol):
    """Repository interface for TaskDependency entities."""
    
    def save(self, dependency: TaskDependency) -> None:
        """Save a dependency."""
        ...
    
    def find_by_id(self, dependency_id: UUID) -> Optional[TaskDependency]:
        """Find dependency by ID."""
        ...
    
    def find_by_task_id(self, task_id: UUID) -> List[TaskDependency]:
        """Find all dependencies for a task."""
        ...
    
    def find_by_depends_on_task_id(self, depends_on_task_id: UUID) -> List[TaskDependency]:
        """Find all tasks that depend on the given task."""
        ...
    
    def delete(self, dependency_id: UUID) -> None:
        """Delete a dependency."""
        ...
