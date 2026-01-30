"""Integration tests for v3.0 workflows.

These tests verify complete business workflows spanning multiple
domain entities and use cases.
"""
import pytest
from datetime import datetime, UTC
from uuid import uuid4

from app.domain.models.task import Task, VALID_TRANSITIONS
from app.domain.models.project_member import ProjectMember
from app.domain.models.task_assignment_history import TaskAssignmentHistory
from app.domain.models.task_abandonment import TaskAbandonment
from app.domain.models.user import User
from app.domain.models.enums import (
    TaskStatus,
    TaskPriority,
    ProjectMemberRole,
    RoleLevel,
    AbandonmentType,
    AssignmentAction,
    WorkloadStatus,
)
from app.domain.services.workload_calculator import WorkloadCalculator
from app.domain.exceptions import BusinessRuleViolation


class TestManagerCreateTaskSetDifficultyEmployeeClaimsCompletes:
    """
    Test workflow: Manager creates task -> Sets difficulty -> Employee claims -> Completes
    """

    def test_full_workflow(self):
        """Test the complete happy path workflow."""
        project_id = uuid4()
        manager_id = uuid4()
        employee_id = uuid4()
        role_id = uuid4()

        # 1. Manager creates a project member for themselves
        manager = ProjectMember.create_manager(
            project_id=project_id,
            user_id=manager_id,
        )
        assert manager.is_manager() is True

        # 2. Employee joins project
        employee = ProjectMember.create_employee(
            project_id=project_id,
            user_id=employee_id,
            level=RoleLevel.MID,
        )
        assert employee.is_employee() is True

        # 3. Manager creates task (without difficulty initially)
        task = Task.create(
            project_id=project_id,
            title="Implement feature X",
            description="Details here",
            role_responsible_id=role_id,
        )
        assert task.difficulty is None
        assert task.can_be_selected() is False

        # 4. Manager sets difficulty
        task.set_difficulty(5)
        assert task.difficulty == 5
        assert task.can_be_selected() is True

        # 5. Employee claims task
        user = User(
            id=employee_id,
            email="employee@test.com",
            name="Employee",
        )
        task.claim(user, [role_id])
        assert task.user_responsible_id == employee_id
        assert task.status == TaskStatus.DOING

        # 6. Record assignment history
        history = TaskAssignmentHistory.record_started(
            task_id=task.id,
            user_id=employee_id,
        )
        assert history.action == AssignmentAction.STARTED

        # 7. Employee completes task
        task.update_status(TaskStatus.DONE)
        assert task.status == TaskStatus.DONE
        assert task.completed_at is not None

        # 8. Record completion
        completion_history = TaskAssignmentHistory.record_completed(
            task_id=task.id,
            user_id=employee_id,
        )
        assert completion_history.action == AssignmentAction.COMPLETED


class TestEmployeeClaimsGetsFiredFromTask:
    """
    Test workflow: Employee claims -> Gets fired from task -> Task returns to TODO
    """

    def test_fired_from_task_workflow(self):
        """Test that firing employee from task properly abandons it."""
        project_id = uuid4()
        manager_id = uuid4()
        employee_id = uuid4()
        role_id = uuid4()

        # Setup: Employee claims a task
        task = Task.create(
            project_id=project_id,
            title="Task to be abandoned",
            description="Details",
            role_responsible_id=role_id,
            difficulty=3,
        )
        user = User(id=employee_id, email="test@test.com", name="Test")
        task.claim(user, [role_id])
        assert task.status == TaskStatus.DOING
        assert task.user_responsible_id == employee_id

        # Manager fires employee from task
        task.abandon()

        assert task.status == TaskStatus.TODO
        assert task.user_responsible_id is None

        # Record abandonment
        abandonment = TaskAbandonment.fired_from_task(
            task_id=task.id,
            user_id=employee_id,
            manager_id=manager_id,
            reason="Reassigning to different team",
        )
        assert abandonment.abandonment_type == AbandonmentType.FIRED_FROM_TASK
        assert abandonment.initiated_by_user_id == manager_id

        # Record assignment history
        history = TaskAssignmentHistory.record_abandoned(
            task_id=task.id,
            user_id=employee_id,
            abandonment_type=AbandonmentType.FIRED_FROM_TASK,
        )
        assert history.action == AssignmentAction.ABANDONED


class TestWorkloadBlockingAssignment:
    """
    Test workflow: Workload blocking - Assignment rejected when would become IMPOSSIBLE
    """

    def _create_doing_task(self, project_id: uuid4, difficulty: int) -> Task:
        """Helper to create a DOING task."""
        task = Task.create(
            project_id=project_id,
            title=f"Task with difficulty {difficulty}",
            description="Test",
            role_responsible_id=uuid4(),
            difficulty=difficulty,
        )
        task.status = TaskStatus.DOING
        return task

    def test_workload_blocks_impossible_assignment(self):
        """Test that assignment is blocked when workload would be impossible."""
        project_id = uuid4()
        employee_id = uuid4()

        # Employee is a MID level (capacity=10)
        employee = ProjectMember.create_employee(
            project_id=project_id,
            user_id=employee_id,
            level=RoleLevel.MID,
        )

        # Current workload: 10 (at capacity)
        current_tasks = [self._create_doing_task(project_id, 10)]

        # Try to add a task with difficulty 8
        new_task = Task.create(
            project_id=project_id,
            title="New task",
            description="Test",
            role_responsible_id=uuid4(),
            difficulty=8,
        )

        # Would be impossible: 10 + 8 = 18, capacity = 10, ratio = 1.8 > 1.5
        would_be_impossible = WorkloadCalculator.would_be_impossible(
            current_tasks=current_tasks,
            new_task=new_task,
            base_capacity=10,
            level=employee.level,
        )

        assert would_be_impossible is True

    def test_workload_allows_acceptable_assignment(self):
        """Test that assignment is allowed when workload remains acceptable."""
        project_id = uuid4()
        employee_id = uuid4()

        # Employee is a SENIOR level (capacity=13)
        employee = ProjectMember.create_employee(
            project_id=project_id,
            user_id=employee_id,
            level=RoleLevel.SENIOR,
        )

        # Current workload: 5
        current_tasks = [self._create_doing_task(project_id, 5)]

        # Try to add a task with difficulty 5
        new_task = Task.create(
            project_id=project_id,
            title="New task",
            description="Test",
            role_responsible_id=uuid4(),
            difficulty=5,
        )

        # Would be fine: 5 + 5 = 10, capacity = 13, ratio = 0.77 -> HEALTHY
        would_be_impossible = WorkloadCalculator.would_be_impossible(
            current_tasks=current_tasks,
            new_task=new_task,
            base_capacity=10,
            level=employee.level,
        )

        assert would_be_impossible is False

    def test_junior_has_lower_capacity(self):
        """Test that junior employees have lower capacity threshold."""
        project_id = uuid4()

        # JUNIOR level (capacity=6)
        junior = ProjectMember.create_employee(
            project_id=project_id,
            user_id=uuid4(),
            level=RoleLevel.JUNIOR,
        )

        # Current workload: 5
        current_tasks = [self._create_doing_task(project_id, 5)]

        # Try to add a task with difficulty 5
        new_task = Task.create(
            project_id=project_id,
            title="New task",
            description="Test",
            role_responsible_id=uuid4(),
            difficulty=5,
        )

        # Would be impossible for junior: 5 + 5 = 10, capacity = 6, ratio = 1.67 > 1.5
        would_be_impossible = WorkloadCalculator.would_be_impossible(
            current_tasks=current_tasks,
            new_task=new_task,
            base_capacity=10,
            level=junior.level,
        )

        assert would_be_impossible is True


class TestManagerCannotClaimTasks:
    """Test that managers cannot claim tasks (BR-PROJ-002)."""

    def test_manager_is_manager(self):
        """Test that manager role is correctly identified."""
        manager = ProjectMember.create_manager(
            project_id=uuid4(),
            user_id=uuid4(),
        )
        assert manager.is_manager() is True
        assert manager.is_employee() is False


class TestTaskStatusTransitionsV3:
    """Test v3.0 task status transitions including CANCELLED."""

    def test_all_paths_to_cancelled(self):
        """Test all valid paths to CANCELLED state."""
        role_id = uuid4()

        # TODO -> CANCELLED
        task1 = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=role_id,
        )
        task1.cancel()
        assert task1.status == TaskStatus.CANCELLED

        # DOING -> CANCELLED
        task2 = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=role_id,
        )
        task2.status = TaskStatus.DOING
        task2.cancel()
        assert task2.status == TaskStatus.CANCELLED

        # BLOCKED -> CANCELLED
        task3 = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=role_id,
        )
        task3.block("Blocked")
        task3.cancel()
        assert task3.status == TaskStatus.CANCELLED

    def test_terminal_states_are_terminal(self):
        """Test that DONE and CANCELLED are both terminal."""
        role_id = uuid4()

        # DONE is terminal
        done_task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=role_id,
        )
        done_task.status = TaskStatus.DONE
        done_task.completed_at = datetime.now(UTC)

        with pytest.raises(BusinessRuleViolation) as exc:
            done_task.update_status(TaskStatus.TODO)
        assert exc.value.code == "done_is_terminal"

        # CANCELLED is terminal
        cancelled_task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=role_id,
        )
        cancelled_task.cancel()

        with pytest.raises(BusinessRuleViolation) as exc:
            cancelled_task.update_status(TaskStatus.TODO)
        assert exc.value.code == "cancelled_is_terminal"


class TestDifficultyRequiredForClaiming:
    """Test that difficulty must be set before task can be claimed (BR-TASK-002)."""

    def test_task_without_difficulty_cannot_be_selected(self):
        """Test task without difficulty cannot be selected."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )

        assert task.difficulty is None
        assert task.can_be_selected() is False

    def test_task_with_difficulty_can_be_selected(self):
        """Test task with difficulty can be selected."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
            difficulty=5,
        )

        assert task.difficulty == 5
        assert task.can_be_selected() is True

    def test_difficulty_range_validation(self):
        """Test difficulty must be between 1-10."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )

        # Valid range
        task.set_difficulty(1)
        assert task.difficulty == 1

        task.set_difficulty(10)
        assert task.difficulty == 10

        # Invalid: too low
        with pytest.raises(BusinessRuleViolation) as exc:
            task.set_difficulty(0)
        assert exc.value.code == "invalid_difficulty"

        # Invalid: too high
        with pytest.raises(BusinessRuleViolation) as exc:
            task.set_difficulty(11)
        assert exc.value.code == "invalid_difficulty"
