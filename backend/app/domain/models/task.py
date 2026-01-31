"""Task domain model."""
from dataclasses import dataclass, field
from typing import Optional

from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import TaskStatus
from app.domain.models.value_objects import ProjectId, RoleId, TaskId, UserId, UtcDateTime


VALID_TRANSITIONS = {
    TaskStatus.TODO: [TaskStatus.DOING, TaskStatus.BLOCKED, TaskStatus.CANCELLED],
    TaskStatus.BLOCKED: [TaskStatus.TODO, TaskStatus.CANCELLED],
    TaskStatus.DOING: [TaskStatus.DONE, TaskStatus.TODO, TaskStatus.BLOCKED, TaskStatus.CANCELLED],
    TaskStatus.DONE: [],
    TaskStatus.CANCELLED: [],
}


@dataclass
class Task:
    """Task entity."""
    id: TaskId
    project_id: ProjectId
    title: str
    description: Optional[str]
    status: TaskStatus
    difficulty: Optional[int]
    role_id: Optional[RoleId]
    assigned_to: Optional[UserId]
    expected_start_date: Optional[UtcDateTime]
    expected_end_date: Optional[UtcDateTime]
    actual_start_date: Optional[UtcDateTime]
    actual_end_date: Optional[UtcDateTime]
    created_at: UtcDateTime = field(default_factory=UtcDateTime.now)

    @classmethod
    def create(
        cls,
        project_id: ProjectId,
        title: str,
        description: Optional[str] = None,
    ) -> "Task":
        """Create a new task."""
        return cls(
            id=TaskId(),
            project_id=project_id,
            title=title.strip(),
            description=description,
            status=TaskStatus.TODO,
            difficulty=None,
            role_id=None,
            assigned_to=None,
            expected_start_date=None,
            expected_end_date=None,
            actual_start_date=None,
            actual_end_date=None,
        )

    def can_transition_to(self, new_status: TaskStatus) -> bool:
        """Check if transition is valid per BR-TASK-003."""
        return new_status in VALID_TRANSITIONS.get(self.status, [])

    def transition_to(self, new_status: TaskStatus) -> None:
        """Transition task status if allowed."""
        if not self.can_transition_to(new_status):
            raise BusinessRuleViolation(
                f"Invalid transition from {self.status} to {new_status}",
                code="invalid_task_transition",
            )
        self.status = new_status
