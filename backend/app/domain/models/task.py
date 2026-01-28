"""Task domain model with business rules."""
from datetime import datetime, UTC
from typing import Optional
from uuid import UUID, uuid4

from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import TaskStatus, TaskPriority, CompletionSource
from app.domain.models.user import User


class Task:
    """Task entity with business logic (BR-002, BR-004-BR-007, BR-018)."""
    
    def __init__(
        self,
        id: UUID,
        project_id: UUID,
        title: str,
        description: str,
        role_responsible_id: UUID,
        status: TaskStatus = TaskStatus.TODO,
        priority: TaskPriority = TaskPriority.MEDIUM,
        rank_index: float = 1.0,
        user_responsible_id: Optional[UUID] = None,
        completion_percentage: Optional[int] = None,
        completion_source: Optional[CompletionSource] = None,
        due_date: Optional[datetime] = None,
        blocked_reason: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
    ):
        self.id = id
        self.project_id = project_id
        self.title = title
        self.description = description
        self.role_responsible_id = role_responsible_id
        self.status = status
        self.priority = priority
        self.rank_index = rank_index
        self.user_responsible_id = user_responsible_id
        self.completion_percentage = completion_percentage
        self.completion_source = completion_source
        self.due_date = due_date
        self.blocked_reason = blocked_reason
        self.created_at = created_at or datetime.now(UTC)
        self.updated_at = updated_at or datetime.now(UTC)
        self.completed_at = completed_at
    
    @classmethod
    def create(
        cls,
        project_id: UUID,
        title: str,
        description: str,
        role_responsible_id: UUID,
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: Optional[datetime] = None,
        rank_index: float = 1.0,
    ) -> "Task":
        """Create a new task (BR-005)."""
        return cls(
            id=uuid4(),
            project_id=project_id,
            title=title,
            description=description,
            role_responsible_id=role_responsible_id,
            status=TaskStatus.TODO,
            priority=priority,
            rank_index=rank_index,
            user_responsible_id=None,
            completion_percentage=None,
            completion_source=None,
            due_date=due_date,
        )
    
    def claim(self, user: User, user_roles: list[UUID]) -> None:
        """
        Claim a task (BR-002, BR-006).
        
        Raises BusinessRuleViolation if:
        - User doesn't have the required role
        - Task is already claimed
        - Task is not in claimable state (todo or blocked)
        """
        # BR-002: User must have the role_responsible role
        if self.role_responsible_id not in user_roles:
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
        
        self.user_responsible_id = user.id
        self.status = TaskStatus.DOING
        self.updated_at = datetime.now(UTC)
    
    def update_status(self, new_status: TaskStatus) -> None:
        """
        Update task status (BR-006, BR-007).
        
        Valid transitions (BR-006):
        - todo → doing, blocked
        - doing → done, blocked
        - blocked → todo
        - done → (terminal, cannot change)
        """
        # BR-007: Done is terminal
        if self.status == TaskStatus.DONE:
            raise BusinessRuleViolation(
                "Cannot change status of completed task",
                code="done_is_terminal"
            )
        
        # Validate transition
        valid_transitions = {
            TaskStatus.TODO: [TaskStatus.DOING, TaskStatus.BLOCKED],
            TaskStatus.DOING: [TaskStatus.DONE, TaskStatus.BLOCKED],
            TaskStatus.BLOCKED: [TaskStatus.TODO],
        }
        
        if new_status not in valid_transitions.get(self.status, []):
            raise BusinessRuleViolation(
                f"Invalid status transition from {self.status} to {new_status}",
                code="invalid_status_transition"
            )
        
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now(UTC)

        # BR-007: Set completed_at when status changes to done
        if new_status == TaskStatus.DONE:
            self.completed_at = datetime.now(UTC)
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
