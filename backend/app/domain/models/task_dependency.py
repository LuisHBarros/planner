"""TaskDependency domain model."""
from dataclasses import dataclass, field

from app.domain.models.enums import DependencyType
from app.domain.models.value_objects import TaskId, UtcDateTime


@dataclass
class TaskDependency:
    """Dependency between tasks."""
    task_id: TaskId
    depends_on_id: TaskId
    dependency_type: DependencyType
    created_at: UtcDateTime = field(default_factory=UtcDateTime.now)

    @classmethod
    def create(
        cls,
        task_id: TaskId,
        depends_on_id: TaskId,
        dependency_type: DependencyType = DependencyType.FINISH_TO_START,
    ) -> "TaskDependency":
        """Create a task dependency."""
        return cls(
            task_id=task_id,
            depends_on_id=depends_on_id,
            dependency_type=dependency_type,
        )
