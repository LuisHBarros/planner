"""Task dependency domain model."""
from datetime import datetime, UTC
from typing import Optional
from uuid import UUID, uuid4

from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import DependencyType


class TaskDependency:
    """Task dependency entity (BR-008, BR-009)."""

    def __init__(
        self,
        id: UUID,
        task_id: UUID,
        depends_on_task_id: UUID,
        dependency_type: DependencyType = DependencyType.BLOCKS,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.task_id = task_id
        self.depends_on_task_id = depends_on_task_id
        self.dependency_type = dependency_type
        self.created_at = created_at or datetime.now(UTC)

    @classmethod
    def create(
        cls,
        task_id: UUID,
        depends_on_task_id: UUID,
        dependency_type: DependencyType = DependencyType.BLOCKS,
    ) -> "TaskDependency":
        """
        Create a new task dependency.

        Raises BusinessRuleViolation if:
        - task_id == depends_on_task_id (self-dependency)
        """
        # BR-008: No self-dependencies
        if task_id == depends_on_task_id:
            raise BusinessRuleViolation(
                "Task cannot depend on itself",
                code="self_dependency",
            )

        return cls(
            id=uuid4(),
            task_id=task_id,
            depends_on_task_id=depends_on_task_id,
            dependency_type=dependency_type,
        )
