"""Unit tests for Task domain model (v3.0)."""
import pytest
from datetime import datetime, UTC
from uuid import uuid4

from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.task import Task, VALID_TRANSITIONS
from app.domain.models.enums import TaskStatus, TaskPriority
from app.domain.models.user import User


class TestTaskCreation:
    """Test task creation (BR-005)."""
    
    def test_create_task_with_defaults(self):
        """Test creating a task with default values."""
        project_id = uuid4()
        role_id = uuid4()
        
        task = Task.create(
            project_id=project_id,
            title="Test Task",
            description="Test description",
            role_responsible_id=role_id,
        )
        
        assert task.status == TaskStatus.TODO
        assert task.priority == TaskPriority.MEDIUM
        assert task.user_responsible_id is None
        assert task.completion_percentage is None
        assert task.rank_index == 1.0
    
    def test_create_task_with_custom_values(self):
        """Test creating a task with custom values."""
        project_id = uuid4()
        role_id = uuid4()
        
        task = Task.create(
            project_id=project_id,
            title="Test Task",
            description="Test description",
            role_responsible_id=role_id,
            priority=TaskPriority.HIGH,
            rank_index=5.0,
        )
        
        assert task.priority == TaskPriority.HIGH
        assert task.rank_index == 5.0


class TestTaskClaiming:
    """Test task claiming (BR-002, BR-006)."""
    
    def test_claim_task_success(self):
        """Test successfully claiming a task."""
        project_id = uuid4()
        role_id = uuid4()
        user = User.create("test@example.com", "Test User")
        
        task = Task.create(
            project_id=project_id,
            title="Test Task",
            description="Test",
            role_responsible_id=role_id,
        )
        
        task.claim(user, [role_id])
        
        assert task.user_responsible_id == user.id
        assert task.status == TaskStatus.DOING
    
    def test_claim_task_wrong_role(self):
        """Test claiming task without required role."""
        project_id = uuid4()
        role_id = uuid4()
        other_role_id = uuid4()
        user = User.create("test@example.com", "Test User")
        
        task = Task.create(
            project_id=project_id,
            title="Test Task",
            description="Test",
            role_responsible_id=role_id,
        )
        
        with pytest.raises(BusinessRuleViolation) as exc:
            task.claim(user, [other_role_id])
        
        assert exc.value.code == "user_missing_role"
    
    def test_claim_already_claimed_task(self):
        """Test claiming an already claimed task."""
        project_id = uuid4()
        role_id = uuid4()
        user1 = User.create("user1@example.com", "User 1")
        user2 = User.create("user2@example.com", "User 2")
        
        task = Task.create(
            project_id=project_id,
            title="Test Task",
            description="Test",
            role_responsible_id=role_id,
        )
        
        task.claim(user1, [role_id])
        
        with pytest.raises(BusinessRuleViolation) as exc:
            task.claim(user2, [role_id])
        
        assert exc.value.code == "task_already_claimed"
    
    def test_claim_blocked_task(self):
        """Test claiming a blocked task (should work)."""
        project_id = uuid4()
        role_id = uuid4()
        user = User.create("test@example.com", "Test User")
        
        task = Task.create(
            project_id=project_id,
            title="Test Task",
            description="Test",
            role_responsible_id=role_id,
        )
        task.block("Waiting on dependency")
        
        task.claim(user, [role_id])
        
        assert task.user_responsible_id == user.id
        assert task.status == TaskStatus.DOING


class TestTaskStatusTransitions:
    """Test task status transitions (BR-006, BR-007)."""
    
    def test_valid_transitions_todo_to_doing(self):
        """Test valid transition: todo → doing."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        
        task.update_status(TaskStatus.DOING)
        assert task.status == TaskStatus.DOING
    
    def test_valid_transitions_todo_to_blocked(self):
        """Test valid transition: todo → blocked."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        
        task.update_status(TaskStatus.BLOCKED)
        assert task.status == TaskStatus.BLOCKED
    
    def test_valid_transitions_doing_to_done(self):
        """Test valid transition: doing → done."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        task.status = TaskStatus.DOING
        
        task.update_status(TaskStatus.DONE)
        
        assert task.status == TaskStatus.DONE
        assert task.completed_at is not None
        assert task.completion_percentage == 100
    
    def test_valid_transitions_blocked_to_todo(self):
        """Test valid transition: blocked → todo."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        task.status = TaskStatus.BLOCKED
        
        task.update_status(TaskStatus.TODO)
        assert task.status == TaskStatus.TODO
    
    def test_invalid_transition_done_to_doing(self):
        """Test invalid transition: done → doing (done is terminal)."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        task.status = TaskStatus.DONE
        task.completed_at = datetime.now(UTC)
        
        with pytest.raises(BusinessRuleViolation) as exc:
            task.update_status(TaskStatus.DOING)
        
        assert exc.value.code == "done_is_terminal"
    
    def test_invalid_transition_todo_to_done(self):
        """Test invalid transition: todo → done (must go through doing)."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        
        with pytest.raises(BusinessRuleViolation) as exc:
            task.update_status(TaskStatus.DONE)
        
        assert exc.value.code == "invalid_status_transition"


class TestTaskBlocking:
    """Test task blocking (BR-006)."""
    
    def test_block_todo_task(self):
        """Test blocking a todo task."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        
        task.block("Waiting on dependency")
        
        assert task.status == TaskStatus.BLOCKED
        assert task.blocked_reason == "Waiting on dependency"
    
    def test_block_doing_task(self):
        """Test blocking a doing task."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        task.status = TaskStatus.DOING
        
        task.block("Encountered blocker")
        
        assert task.status == TaskStatus.BLOCKED
    
    def test_unblock_task(self):
        """Test unblocking a task."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        task.block("Waiting")
        
        task.unblock()
        
        assert task.status == TaskStatus.TODO
        assert task.blocked_reason is None


class TestTaskProgress:
    """Test manual progress tracking (BR-018)."""
    
    def test_set_manual_progress_success(self):
        """Test setting manual progress successfully."""
        project_id = uuid4()
        role_id = uuid4()
        user = User.create("test@example.com", "Test User")
        
        task = Task.create(
            project_id=project_id,
            title="Test",
            description="Test",
            role_responsible_id=role_id,
        )
        task.claim(user, [role_id])
        
        task.set_manual_progress(50)
        
        assert task.completion_percentage == 50
        assert task.completion_source.value == "manual"
    
    def test_set_progress_invalid_percentage(self):
        """Test setting invalid progress percentage."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        task.status = TaskStatus.DOING
        
        with pytest.raises(BusinessRuleViolation) as exc:
            task.set_manual_progress(150)
        
        assert exc.value.code == "invalid_percentage"
    
    def test_set_progress_done_task(self):
        """Test setting progress for done task (should fail)."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        task.status = TaskStatus.DONE
        task.completed_at = datetime.now(UTC)
        
        with pytest.raises(BusinessRuleViolation) as exc:
            task.set_manual_progress(50)
        
        assert exc.value.code == "done_task_progress"
    
    def test_set_progress_unclaimed_todo_task(self):
        """Test setting progress for unclaimed todo task (should fail)."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )

        with pytest.raises(BusinessRuleViolation) as exc:
            task.set_manual_progress(50)

        assert exc.value.code == "unclaimed_task_progress"


# v3.0 Tests


class TestTaskDifficulty:
    """Test task difficulty (BR-TASK-002)."""

    def test_create_task_with_difficulty(self):
        """Test creating a task with difficulty."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
            difficulty=5,
        )
        assert task.difficulty == 5

    def test_create_task_without_difficulty(self):
        """Test creating a task without difficulty defaults to None."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        assert task.difficulty is None

    def test_set_difficulty_valid(self):
        """Test setting valid difficulty."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        task.set_difficulty(7)
        assert task.difficulty == 7

    def test_set_difficulty_min_value(self):
        """Test setting minimum difficulty value."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        task.set_difficulty(1)
        assert task.difficulty == 1

    def test_set_difficulty_max_value(self):
        """Test setting maximum difficulty value."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        task.set_difficulty(10)
        assert task.difficulty == 10

    def test_set_difficulty_below_min(self):
        """Test setting difficulty below minimum."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        with pytest.raises(BusinessRuleViolation) as exc:
            task.set_difficulty(0)
        assert exc.value.code == "invalid_difficulty"

    def test_set_difficulty_above_max(self):
        """Test setting difficulty above maximum."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        with pytest.raises(BusinessRuleViolation) as exc:
            task.set_difficulty(11)
        assert exc.value.code == "invalid_difficulty"

    def test_set_difficulty_on_done_task(self):
        """Test setting difficulty on completed task (should fail)."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        task.status = TaskStatus.DONE
        task.completed_at = datetime.now(UTC)

        with pytest.raises(BusinessRuleViolation) as exc:
            task.set_difficulty(5)
        assert exc.value.code == "task_is_terminal"

    def test_set_difficulty_on_cancelled_task(self):
        """Test setting difficulty on cancelled task (should fail)."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        task.cancel()

        with pytest.raises(BusinessRuleViolation) as exc:
            task.set_difficulty(5)
        assert exc.value.code == "task_is_terminal"


class TestCanBeSelected:
    """Test can_be_selected method (BR-TASK-002)."""

    def test_can_be_selected_with_difficulty(self):
        """Test task with difficulty can be selected."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
            difficulty=5,
        )
        assert task.can_be_selected() is True

    def test_cannot_be_selected_without_difficulty(self):
        """Test task without difficulty cannot be selected."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        assert task.can_be_selected() is False


class TestTaskCancellation:
    """Test task cancellation (v3.0)."""

    def test_cancel_todo_task(self):
        """Test cancelling a todo task."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        task.cancel("No longer needed")

        assert task.status == TaskStatus.CANCELLED
        assert task.cancellation_reason == "No longer needed"
        assert task.cancelled_at is not None

    def test_cancel_doing_task(self):
        """Test cancelling a doing task."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        task.status = TaskStatus.DOING

        task.cancel()

        assert task.status == TaskStatus.CANCELLED

    def test_cancel_blocked_task(self):
        """Test cancelling a blocked task."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        task.block("Blocked")

        task.cancel()

        assert task.status == TaskStatus.CANCELLED

    def test_cancel_done_task_fails(self):
        """Test cancelling a done task (should fail)."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        task.status = TaskStatus.DONE
        task.completed_at = datetime.now(UTC)

        with pytest.raises(BusinessRuleViolation) as exc:
            task.cancel()
        assert exc.value.code == "done_is_terminal"

    def test_cancel_already_cancelled_fails(self):
        """Test cancelling an already cancelled task (should fail)."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        task.cancel()

        with pytest.raises(BusinessRuleViolation) as exc:
            task.cancel()
        assert exc.value.code == "already_cancelled"


class TestTaskAbandonment:
    """Test task abandonment (v3.0)."""

    def test_abandon_doing_task(self):
        """Test abandoning a doing task."""
        user = User.create("test@example.com", "Test User")
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        task.status = TaskStatus.DOING
        task.user_responsible_id = user.id

        task.abandon()

        assert task.status == TaskStatus.TODO
        assert task.user_responsible_id is None

    def test_abandon_todo_task_fails(self):
        """Test abandoning a todo task (should fail)."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )

        with pytest.raises(BusinessRuleViolation) as exc:
            task.abandon()
        assert exc.value.code == "invalid_status_for_abandon"

    def test_abandon_done_task_fails(self):
        """Test abandoning a done task (should fail)."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        task.status = TaskStatus.DONE

        with pytest.raises(BusinessRuleViolation) as exc:
            task.abandon()
        assert exc.value.code == "invalid_status_for_abandon"


class TestValidTransitionsV3:
    """Test v3.0 valid transitions including CANCELLED."""

    def test_todo_can_transition_to_cancelled(self):
        """Test todo -> cancelled is valid."""
        assert TaskStatus.CANCELLED in VALID_TRANSITIONS[TaskStatus.TODO]

    def test_doing_can_transition_to_cancelled(self):
        """Test doing -> cancelled is valid."""
        assert TaskStatus.CANCELLED in VALID_TRANSITIONS[TaskStatus.DOING]

    def test_doing_can_transition_to_todo(self):
        """Test doing -> todo is valid (for abandonment)."""
        assert TaskStatus.TODO in VALID_TRANSITIONS[TaskStatus.DOING]

    def test_blocked_can_transition_to_cancelled(self):
        """Test blocked -> cancelled is valid."""
        assert TaskStatus.CANCELLED in VALID_TRANSITIONS[TaskStatus.BLOCKED]

    def test_cancelled_is_terminal(self):
        """Test cancelled has no valid transitions (terminal)."""
        assert VALID_TRANSITIONS[TaskStatus.CANCELLED] == []

    def test_done_is_terminal(self):
        """Test done has no valid transitions (terminal)."""
        assert VALID_TRANSITIONS[TaskStatus.DONE] == []

    def test_cannot_transition_from_cancelled(self):
        """Test transitioning from cancelled fails."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        task.cancel()

        with pytest.raises(BusinessRuleViolation) as exc:
            task.update_status(TaskStatus.TODO)
        assert exc.value.code == "cancelled_is_terminal"
