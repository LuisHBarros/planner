"""Task domain model with business rules."""
from datetime import datetime, UTC
from typing import Optional, Union
from uuid import UUID

from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import TaskStatus, TaskPriority, CompletionSource
from app.domain.models.user import User
from app.domain.models.value_objects import TaskId, ProjectId, RoleId, UserId


# Valid status transitions (BR-006, v3.0)
VALID_TRANSITIONS = {
    TaskStatus.TODO: [TaskStatus.DOING, TaskStatus.BLOCKED, TaskStatus.CANCELLED],
    TaskStatus.DOING: [TaskStatus.DONE, TaskStatus.TODO, TaskStatus.BLOCKED, TaskStatus.CANCELLED],
    TaskStatus.BLOCKED: [TaskStatus.TODO, TaskStatus.CANCELLED],
    TaskStatus.DONE: [],  # Terminal
    TaskStatus.CANCELLED: [],  # Terminal
}


class Task:
    """Task entity with business logic (BR-002, BR-004-BR-007, BR-018).

    Uses value objects for type-safe identifiers per architecture_guide.md v2.1.
    """

    def __init__(
        self,
        id: Union[TaskId, UUID],
        project_id: Union[ProjectId, UUID],
        title: str,
        description: str,
        role_responsible_id: Union[RoleId, UUID],
        status: TaskStatus = TaskStatus.TODO,
        priority: TaskPriority = TaskPriority.MEDIUM,
        rank_index: float = 1.0,
        user_responsible_id: Optional[Union[UserId, UUID]] = None,
        difficulty: Optional[int] = None,  # v3.0: 1-10, required for selection (BR-TASK-002)
        completion_percentage: Optional[int] = None,
        completion_source: Optional[CompletionSource] = None,
        due_date: Optional[datetime] = None,
        expected_start_date: Optional[datetime] = None,
        expected_end_date: Optional[datetime] = None,
        actual_start_date: Optional[datetime] = None,
        actual_end_date: Optional[datetime] = None,
        is_delayed: bool = False,
        blocked_reason: Optional[str] = None,
        cancellation_reason: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        cancelled_at: Optional[datetime] = None,
    ):
        # Convert raw UUIDs to value objects for type safety
        self.id = id if isinstance(id, TaskId) else TaskId(id)
        self.project_id = project_id if isinstance(project_id, ProjectId) else ProjectId(project_id)
        self.role_responsible_id = (
            role_responsible_id if isinstance(role_responsible_id, RoleId)
            else RoleId(role_responsible_id)
        )
        self.user_responsible_id = (
            user_responsible_id if user_responsible_id is None or isinstance(user_responsible_id, UserId)
            else UserId(user_responsible_id)
        )
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.rank_index = rank_index
        self.difficulty = difficulty
        self.completion_percentage = completion_percentage
        self.completion_source = completion_source
        self.due_date = due_date
        self.expected_start_date = expected_start_date
        self.expected_end_date = expected_end_date
        self.actual_start_date = actual_start_date
        self.actual_end_date = actual_end_date
        self.is_delayed = is_delayed
        self.blocked_reason = blocked_reason
        self.cancellation_reason = cancellation_reason
        self.created_at = created_at or datetime.now(UTC)
        self.updated_at = updated_at or datetime.now(UTC)
        self.completed_at = completed_at
        self.cancelled_at = cancelled_at
    
    @classmethod
    def create(
        cls,
        project_id: Union[ProjectId, UUID],
        title: str,
        description: str,
        role_responsible_id: Union[RoleId, UUID],
        priority: TaskPriority = TaskPriority.MEDIUM,
        difficulty: Optional[int] = None,
        due_date: Optional[datetime] = None,
        expected_start_date: Optional[datetime] = None,
        expected_end_date: Optional[datetime] = None,
        rank_index: float = 1.0,
    ) -> "Task":
        """Create a new task (BR-005)."""
        return cls(
            id=TaskId(),  # Generate new TaskId
            project_id=project_id,
            title=title,
            description=description,
            role_responsible_id=role_responsible_id,
            status=TaskStatus.TODO,
            priority=priority,
            rank_index=rank_index,
            user_responsible_id=None,
            difficulty=difficulty,
            completion_percentage=None,
            completion_source=None,
            due_date=due_date,
            expected_start_date=expected_start_date,
            expected_end_date=expected_end_date,
            actual_start_date=None,
            actual_end_date=None,
            is_delayed=False,
        )

    def can_be_selected(self) -> bool:
        """
        Check if task can be selected/claimed (BR-TASK-002).

        Returns False if difficulty is None (must be set before selection).
        """
        return self.difficulty is not None

    def set_difficulty(self, difficulty: int) -> None:
        """
        Set task difficulty (1-10 scale).

        Raises BusinessRuleViolation if:
        - Difficulty is not in valid range
        - Task is in terminal state
        """
        if not (1 <= difficulty <= 10):
            raise BusinessRuleViolation(
                "Difficulty must be between 1 and 10",
                code="invalid_difficulty"
            )

        if self.status in [TaskStatus.DONE, TaskStatus.CANCELLED]:
            raise BusinessRuleViolation(
                "Cannot set difficulty for completed or cancelled task",
                code="task_is_terminal"
            )

        self.difficulty = difficulty
        self.updated_at = datetime.now(UTC)

    def cancel(self, reason: Optional[str] = None) -> None:
        """
        Cancel a task (v3.0).

        Raises BusinessRuleViolation if:
        - Task is already in terminal state (DONE or CANCELLED)
        """
        if self.status == TaskStatus.DONE:
            raise BusinessRuleViolation(
                "Cannot cancel completed task",
                code="done_is_terminal"
            )

        if self.status == TaskStatus.CANCELLED:
            raise BusinessRuleViolation(
                "Task is already cancelled",
                code="already_cancelled"
            )

        self.status = TaskStatus.CANCELLED
        self.cancellation_reason = reason
        self.cancelled_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)

    def abandon(self) -> None:
        """
        Abandon a task (v3.0).

        Resets task to TODO status and clears user_responsible_id.
        Only allowed when task is DOING.

        Raises BusinessRuleViolation if task is not in DOING status.
        """
        if self.status != TaskStatus.DOING:
            raise BusinessRuleViolation(
                f"Cannot abandon task in status: {self.status}",
                code="invalid_status_for_abandon"
            )

        self.status = TaskStatus.TODO
        self.user_responsible_id = None
        self.updated_at = datetime.now(UTC)
    
    def claim(self, user: User, user_roles: list[Union[RoleId, UUID]]) -> None:
        """
        Claim a task (BR-002, BR-006).

        Raises BusinessRuleViolation if:
        - User doesn't have the required role
        - Task is already claimed
        - Task is not in claimable state (todo or blocked)
        """
        # BR-002: User must have the role_responsible role
        # Compare using .value to handle both RoleId and UUID in user_roles
        role_values = [r.value if isinstance(r, RoleId) else r for r in user_roles]
        if self.role_responsible_id.value not in role_values:
            raise BusinessRuleViolation(
                "User doesn't have required role to claim this task",
                code="user_missing_role"
            )

        # BR-002: Task must not be already claimed
        if self.user_responsible_id is not None:
            raise BusinessRuleViolation(
                "Task already claimed",
                code="task_already_claimed"
            )

        # BR-002: Task must be in claimable state
        if self.status not in [TaskStatus.TODO, TaskStatus.BLOCKED]:
            raise BusinessRuleViolation(
                f"Cannot claim task in status: {self.status}",
                code="invalid_status_for_claim"
            )

        self.user_responsible_id = UserId(user.id) if not isinstance(user.id, UserId) else user.id
        self.status = TaskStatus.DOING
        self.updated_at = datetime.now(UTC)
    
    def update_status(self, new_status: TaskStatus) -> None:
        """
        Update task status (BR-006, BR-007, v3.0).

        Valid transitions (BR-006, v3.0):
        - todo → doing, blocked, cancelled
        - doing → done, todo, blocked, cancelled
        - blocked → todo, cancelled
        - done → (terminal, cannot change)
        - cancelled → (terminal, cannot change)
        """
        # BR-007: Done is terminal
        if self.status == TaskStatus.DONE:
            raise BusinessRuleViolation(
                "Cannot change status of completed task",
                code="done_is_terminal"
            )

        # v3.0: Cancelled is terminal
        if self.status == TaskStatus.CANCELLED:
            raise BusinessRuleViolation(
                "Cannot change status of cancelled task",
                code="cancelled_is_terminal"
            )

        # Validate transition using module-level constant
        if new_status not in VALID_TRANSITIONS.get(self.status, []):
            raise BusinessRuleViolation(
                f"Invalid status transition from {self.status} to {new_status}",
                code="invalid_status_transition"
            )
        
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now(UTC)

        # When task moves to DOING for the first time, set actual_start_date
        if new_status == TaskStatus.DOING and self.actual_start_date is None:
            self.actual_start_date = datetime.now(UTC)

        # BR-007: Set completed_at and actual_end_date when status changes to done
        if new_status == TaskStatus.DONE:
            now = datetime.now(UTC)
            self.completed_at = now
            # Only set actual_start_date if it was never set (edge case: todo -> done)
            if self.actual_start_date is None:
                self.actual_start_date = now
            # Actual end date is immutable once set
            if self.actual_end_date is None:
                self.actual_end_date = now
            self.completion_percentage = 100
            self.completion_source = CompletionSource.MANUAL
    
    def block(self, reason: str) -> None:
        """
        Block a task (BR-006).
        
        Can only block tasks in TODO or DOING status.
        """
        if self.status not in [TaskStatus.TODO, TaskStatus.DOING]:
            raise BusinessRuleViolation(
                f"Cannot block task in status: {self.status}",
                code="invalid_status_for_block"
            )
        
        self.status = TaskStatus.BLOCKED
        self.blocked_reason = reason
        self.updated_at = datetime.now(UTC)
    
    def unblock(self) -> None:
        """
        Unblock a task (BR-009).
        
        Changes status from blocked to todo.
        """
        if self.status != TaskStatus.BLOCKED:
            raise BusinessRuleViolation(
                f"Cannot unblock task in status: {self.status}",
                code="invalid_status_for_unblock"
            )
        
        self.status = TaskStatus.TODO
        self.blocked_reason = None
        self.updated_at = datetime.now(UTC)
    
    def set_manual_progress(self, percentage: int) -> None:
        """
        Set manual progress percentage (BR-018).
        
        Raises BusinessRuleViolation if:
        - Percentage is not between 0-100
        - Task is in done status (always 100%)
        - Task is in todo status (unless claimed)
        """
        if not (0 <= percentage <= 100):
            raise BusinessRuleViolation(
                "Progress percentage must be between 0 and 100",
                code="invalid_percentage"
            )
        
        # BR-018: Cannot set progress for done tasks
        if self.status == TaskStatus.DONE:
            raise BusinessRuleViolation(
                "Cannot set progress for completed tasks",
                code="done_task_progress"
            )
        
        # BR-018: Cannot set progress for unclaimed todo tasks
        if self.status == TaskStatus.TODO and self.user_responsible_id is None:
            raise BusinessRuleViolation(
                "Cannot set progress for unclaimed tasks",
                code="unclaimed_task_progress"
            )
        
        self.completion_percentage = percentage
        self.completion_source = CompletionSource.MANUAL
        self.updated_at = datetime.now(UTC)
