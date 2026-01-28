"""Unit tests for Task domain model."""
import pytest
from datetime import datetime, UTC
from uuid import uuid4

from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.task import Task
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
