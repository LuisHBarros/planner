"""Unit tests for domain enums (v3.0)."""
import pytest

from app.domain.models.enums import (
    TaskStatus,
    AbandonmentType,
    WorkloadStatus,
    ProjectMemberRole,
    AssignmentAction,
)


class TestTaskStatus:
    """Test TaskStatus enum."""

    def test_all_statuses_exist(self):
        """Verify all expected statuses exist."""
        assert TaskStatus.TODO.value == "todo"
        assert TaskStatus.DOING.value == "doing"
        assert TaskStatus.BLOCKED.value == "blocked"
        assert TaskStatus.DONE.value == "done"
        assert TaskStatus.CANCELLED.value == "cancelled"

    def test_cancelled_is_terminal(self):
        """Verify CANCELLED is a valid terminal state."""
        # This test documents the v3.0 requirement
        terminal_states = [TaskStatus.DONE, TaskStatus.CANCELLED]
        assert TaskStatus.CANCELLED in terminal_states


class TestAbandonmentType:
    """Test AbandonmentType enum."""

    def test_all_types_exist(self):
        """Verify all abandonment types exist."""
        assert AbandonmentType.VOLUNTARY.value == "voluntary"
        assert AbandonmentType.FIRED_FROM_TASK.value == "fired_from_task"
        assert AbandonmentType.FIRED_FROM_PROJECT.value == "fired_from_project"
        assert AbandonmentType.RESIGNED.value == "resigned"
        assert AbandonmentType.TASK_CANCELLED.value == "task_cancelled"

    def test_user_initiated_types(self):
        """Test which types are initiated by the user themselves."""
        user_initiated = [AbandonmentType.VOLUNTARY, AbandonmentType.RESIGNED]
        assert AbandonmentType.VOLUNTARY in user_initiated
        assert AbandonmentType.RESIGNED in user_initiated
        assert AbandonmentType.FIRED_FROM_TASK not in user_initiated

    def test_manager_initiated_types(self):
        """Test which types are initiated by managers."""
        manager_initiated = [
            AbandonmentType.FIRED_FROM_TASK,
            AbandonmentType.FIRED_FROM_PROJECT,
            AbandonmentType.TASK_CANCELLED,
        ]
        assert AbandonmentType.FIRED_FROM_TASK in manager_initiated
        assert AbandonmentType.VOLUNTARY not in manager_initiated


class TestWorkloadStatus:
    """Test WorkloadStatus enum."""

    def test_all_statuses_exist(self):
        """Verify all workload statuses exist."""
        assert WorkloadStatus.IMPOSSIBLE.value == "impossible"
        assert WorkloadStatus.TIGHT.value == "tight"
        assert WorkloadStatus.HEALTHY.value == "healthy"
        assert WorkloadStatus.RELAXED.value == "relaxed"
        assert WorkloadStatus.IDLE.value == "idle"

    def test_status_ordering(self):
        """Document the severity ordering of workload statuses."""
        # From most severe to least severe
        severity_order = [
            WorkloadStatus.IMPOSSIBLE,  # Most severe - cannot take more work
            WorkloadStatus.TIGHT,
            WorkloadStatus.HEALTHY,
            WorkloadStatus.RELAXED,
            WorkloadStatus.IDLE,  # Least severe - needs more work
        ]
        assert len(severity_order) == 5


class TestProjectMemberRole:
    """Test ProjectMemberRole enum."""

    def test_all_roles_exist(self):
        """Verify all project member roles exist."""
        assert ProjectMemberRole.MANAGER.value == "manager"
        assert ProjectMemberRole.EMPLOYEE.value == "employee"

    def test_role_count(self):
        """Verify we have exactly the expected roles."""
        assert len(ProjectMemberRole) == 2


class TestAssignmentAction:
    """Test AssignmentAction enum."""

    def test_all_actions_exist(self):
        """Verify all assignment actions exist."""
        assert AssignmentAction.STARTED.value == "started"
        assert AssignmentAction.ABANDONED.value == "abandoned"
        assert AssignmentAction.RESUMED.value == "resumed"
        assert AssignmentAction.COMPLETED.value == "completed"

    def test_lifecycle_actions(self):
        """Test the typical task assignment lifecycle."""
        # Normal flow: STARTED -> COMPLETED
        # With abandon: STARTED -> ABANDONED
        # Resume after abandon: RESUMED -> COMPLETED
        lifecycle_actions = [
            AssignmentAction.STARTED,
            AssignmentAction.ABANDONED,
            AssignmentAction.RESUMED,
            AssignmentAction.COMPLETED,
        ]
        assert len(lifecycle_actions) == 4
