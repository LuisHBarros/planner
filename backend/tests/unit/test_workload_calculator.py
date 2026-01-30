"""Unit tests for WorkloadCalculator (v3.0 BR-WORK-001/002/003)."""
import pytest
from uuid import uuid4

from app.domain.services.workload_calculator import (
    WorkloadCalculator,
    WorkloadResult,
    WorkloadHealth,
    LEVEL_MULTIPLIERS,
    WORKLOAD_THRESHOLDS,
)
from app.domain.models.role import Role
from app.domain.models.task import Task
from app.domain.models.enums import RoleLevel, WorkloadStatus, TaskStatus


class TestLevelMultipliers:
    """Test level multiplier retrieval (BR-WORK-001)."""

    def test_junior_multiplier(self):
        """Test JUNIOR multiplier is 0.6."""
        assert WorkloadCalculator.get_level_multiplier(RoleLevel.JUNIOR) == 0.6

    def test_mid_multiplier(self):
        """Test MID multiplier is 1.0."""
        assert WorkloadCalculator.get_level_multiplier(RoleLevel.MID) == 1.0

    def test_senior_multiplier(self):
        """Test SENIOR multiplier is 1.3."""
        assert WorkloadCalculator.get_level_multiplier(RoleLevel.SENIOR) == 1.3

    def test_specialist_multiplier(self):
        """Test SPECIALIST multiplier is 1.2."""
        assert WorkloadCalculator.get_level_multiplier(RoleLevel.SPECIALIST) == 1.2

    def test_lead_multiplier(self):
        """Test LEAD multiplier is 1.1."""
        assert WorkloadCalculator.get_level_multiplier(RoleLevel.LEAD) == 1.1

    def test_all_levels_have_multipliers(self):
        """Test all role levels have defined multipliers."""
        for level in RoleLevel:
            assert level in LEVEL_MULTIPLIERS


class TestCalculateCapacity:
    """Test capacity calculation (BR-WORK-001)."""

    def test_junior_capacity(self):
        """Test JUNIOR capacity calculation."""
        # base=10, multiplier=0.6 -> 6.0
        assert WorkloadCalculator.calculate_capacity(10, RoleLevel.JUNIOR) == 6.0

    def test_mid_capacity(self):
        """Test MID capacity calculation."""
        # base=10, multiplier=1.0 -> 10.0
        assert WorkloadCalculator.calculate_capacity(10, RoleLevel.MID) == 10.0

    def test_senior_capacity(self):
        """Test SENIOR capacity calculation."""
        # base=10, multiplier=1.3 -> 13.0
        assert WorkloadCalculator.calculate_capacity(10, RoleLevel.SENIOR) == 13.0

    def test_zero_base_capacity(self):
        """Test with zero base capacity."""
        assert WorkloadCalculator.calculate_capacity(0, RoleLevel.MID) == 0.0


class TestCalculateWorkloadScore:
    """Test workload score calculation (BR-WORK-002)."""

    def _create_task(self, difficulty: int, status: TaskStatus = TaskStatus.DOING) -> Task:
        """Helper to create a task with given difficulty and status."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
            difficulty=difficulty,
        )
        task.status = status
        return task

    def test_empty_tasks(self):
        """Test with no tasks."""
        assert WorkloadCalculator.calculate_workload_score([]) == 0

    def test_single_doing_task(self):
        """Test with single DOING task."""
        tasks = [self._create_task(5)]
        assert WorkloadCalculator.calculate_workload_score(tasks) == 5

    def test_multiple_doing_tasks(self):
        """Test with multiple DOING tasks."""
        tasks = [
            self._create_task(3),
            self._create_task(5),
            self._create_task(2),
        ]
        assert WorkloadCalculator.calculate_workload_score(tasks) == 10

    def test_only_counts_doing_tasks(self):
        """Test that only DOING tasks are counted."""
        tasks = [
            self._create_task(5, TaskStatus.DOING),
            self._create_task(3, TaskStatus.TODO),
            self._create_task(2, TaskStatus.DONE),
            self._create_task(4, TaskStatus.BLOCKED),
        ]
        assert WorkloadCalculator.calculate_workload_score(tasks) == 5

    def test_task_without_difficulty(self):
        """Test task without difficulty counts as 1."""
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
        )
        task.status = TaskStatus.DOING
        # difficulty is None
        assert WorkloadCalculator.calculate_workload_score([task]) == 1


class TestCalculateStatus:
    """Test workload status calculation (BR-WORK-002)."""

    def test_impossible_status(self):
        """Test IMPOSSIBLE when ratio > 1.5."""
        # score=16, capacity=10 -> ratio=1.6 > 1.5
        assert WorkloadCalculator.calculate_status(16, 10) == WorkloadStatus.IMPOSSIBLE

    def test_tight_status(self):
        """Test TIGHT when 1.2 < ratio <= 1.5."""
        # score=13, capacity=10 -> ratio=1.3
        assert WorkloadCalculator.calculate_status(13, 10) == WorkloadStatus.TIGHT

    def test_healthy_status(self):
        """Test HEALTHY when 0.7 < ratio <= 1.2."""
        # score=10, capacity=10 -> ratio=1.0
        assert WorkloadCalculator.calculate_status(10, 10) == WorkloadStatus.HEALTHY

    def test_relaxed_status(self):
        """Test RELAXED when 0.3 < ratio <= 0.7."""
        # score=5, capacity=10 -> ratio=0.5
        assert WorkloadCalculator.calculate_status(5, 10) == WorkloadStatus.RELAXED

    def test_idle_status(self):
        """Test IDLE when ratio <= 0.3."""
        # score=2, capacity=10 -> ratio=0.2
        assert WorkloadCalculator.calculate_status(2, 10) == WorkloadStatus.IDLE

    def test_zero_capacity_with_work(self):
        """Test zero capacity with work is IMPOSSIBLE."""
        assert WorkloadCalculator.calculate_status(5, 0) == WorkloadStatus.IMPOSSIBLE

    def test_zero_capacity_no_work(self):
        """Test zero capacity with no work is IDLE."""
        assert WorkloadCalculator.calculate_status(0, 0) == WorkloadStatus.IDLE

    def test_boundary_impossible(self):
        """Test boundary at ratio=1.5 (not IMPOSSIBLE)."""
        # score=15, capacity=10 -> ratio=1.5 (exactly at threshold)
        # Threshold is > 1.5, so 1.5 is TIGHT
        assert WorkloadCalculator.calculate_status(15, 10) == WorkloadStatus.TIGHT

    def test_boundary_tight(self):
        """Test boundary at ratio=1.2 (not TIGHT)."""
        # score=12, capacity=10 -> ratio=1.2
        # Threshold is > 1.2, so 1.2 is HEALTHY
        assert WorkloadCalculator.calculate_status(12, 10) == WorkloadStatus.HEALTHY


class TestCalculateWorkload:
    """Test complete workload calculation."""

    def _create_doing_task(self, difficulty: int) -> Task:
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
            difficulty=difficulty,
        )
        task.status = TaskStatus.DOING
        return task

    def test_complete_workload_calculation(self):
        """Test full workload calculation returns correct result."""
        tasks = [
            self._create_doing_task(5),
            self._create_doing_task(3),
        ]
        # score=8, capacity=10 (MID), ratio=0.8 -> HEALTHY
        result = WorkloadCalculator.calculate_workload(
            tasks=tasks,
            base_capacity=10,
            level=RoleLevel.MID,
        )

        assert result.score == 8
        assert result.capacity == 10.0
        assert result.ratio == 0.8
        assert result.status == WorkloadStatus.HEALTHY


class TestSimulateAssignment:
    """Test workload simulation (BR-ASSIGN-003)."""

    def _create_doing_task(self, difficulty: int) -> Task:
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
            difficulty=difficulty,
        )
        task.status = TaskStatus.DOING
        return task

    def _create_new_task(self, difficulty: int) -> Task:
        return Task.create(
            project_id=uuid4(),
            title="New Task",
            description="Test",
            role_responsible_id=uuid4(),
            difficulty=difficulty,
        )

    def test_simulate_adds_task_difficulty(self):
        """Test simulation adds new task's difficulty."""
        current_tasks = [self._create_doing_task(5)]
        new_task = self._create_new_task(3)

        result = WorkloadCalculator.simulate_assignment(
            current_tasks=current_tasks,
            new_task=new_task,
            base_capacity=10,
            level=RoleLevel.MID,
        )

        # current=5, new=3, total=8
        assert result.score == 8

    def test_simulate_assignment_would_be_impossible(self):
        """Test simulation detects impossible workload."""
        current_tasks = [self._create_doing_task(10)]
        new_task = self._create_new_task(8)

        result = WorkloadCalculator.simulate_assignment(
            current_tasks=current_tasks,
            new_task=new_task,
            base_capacity=10,
            level=RoleLevel.MID,
        )

        # current=10, new=8, total=18, capacity=10, ratio=1.8 > 1.5
        assert result.status == WorkloadStatus.IMPOSSIBLE


class TestWouldBeImpossible:
    """Test would_be_impossible helper (BR-ASSIGN-003)."""

    def _create_doing_task(self, difficulty: int) -> Task:
        task = Task.create(
            project_id=uuid4(),
            title="Test",
            description="Test",
            role_responsible_id=uuid4(),
            difficulty=difficulty,
        )
        task.status = TaskStatus.DOING
        return task

    def _create_new_task(self, difficulty: int) -> Task:
        return Task.create(
            project_id=uuid4(),
            title="New Task",
            description="Test",
            role_responsible_id=uuid4(),
            difficulty=difficulty,
        )

    def test_would_be_impossible_true(self):
        """Test returns True when assignment would exceed capacity."""
        current_tasks = [self._create_doing_task(10)]
        new_task = self._create_new_task(8)

        assert WorkloadCalculator.would_be_impossible(
            current_tasks=current_tasks,
            new_task=new_task,
            base_capacity=10,
            level=RoleLevel.MID,
        ) is True

    def test_would_be_impossible_false(self):
        """Test returns False when assignment is acceptable."""
        current_tasks = [self._create_doing_task(5)]
        new_task = self._create_new_task(3)

        assert WorkloadCalculator.would_be_impossible(
            current_tasks=current_tasks,
            new_task=new_task,
            base_capacity=10,
            level=RoleLevel.MID,
        ) is False

    def test_senior_can_take_more(self):
        """Test senior level has higher capacity threshold."""
        current_tasks = [self._create_doing_task(10)]
        new_task = self._create_new_task(5)

        # MID: capacity=10, total=15, ratio=1.5 -> TIGHT (not impossible)
        # JUNIOR: capacity=6, total=15, ratio=2.5 -> IMPOSSIBLE
        # SENIOR: capacity=13, total=15, ratio=1.15 -> HEALTHY

        assert WorkloadCalculator.would_be_impossible(
            current_tasks=current_tasks,
            new_task=new_task,
            base_capacity=10,
            level=RoleLevel.MID,
        ) is False

        assert WorkloadCalculator.would_be_impossible(
            current_tasks=current_tasks,
            new_task=new_task,
            base_capacity=10,
            level=RoleLevel.JUNIOR,
        ) is True

        assert WorkloadCalculator.would_be_impossible(
            current_tasks=current_tasks,
            new_task=new_task,
            base_capacity=10,
            level=RoleLevel.SENIOR,
        ) is False


class TestLegacyCalculateHealth:
    """Test legacy calculate_health method for backward compatibility."""

    def test_calculate_tranquilo(self):
        """Test calculating tranquilo status."""
        role = Role.create(
            team_id=None,
            name="Backend",
            level=RoleLevel.SENIOR,
            base_capacity=5,
        )

        # tasks_per_person = 3 / 2 = 1.5
        # baseline = 5
        # 1.5 < 5 * 0.8 = 4.0 -> tranquilo
        health = WorkloadCalculator.calculate_health(
            role=role,
            active_tasks=3,
            users_count=2,
            baseline=5.0,
        )

        assert health.status == "tranquilo"
        assert health.tasks_per_person == 1.5

    def test_calculate_saudavel(self):
        """Test calculating saudavel status."""
        role = Role.create(
            team_id=None,
            name="Backend",
            level=RoleLevel.SENIOR,
            base_capacity=5,
        )

        # tasks_per_person = 4 / 1 = 4.0
        # baseline = 5
        # 4.0 >= 4.0 (5*0.8) and 4.0 <= 5.0 -> saudavel
        health = WorkloadCalculator.calculate_health(
            role=role,
            active_tasks=4,
            users_count=1,
            baseline=5.0,
        )

        assert health.status == "saudavel"

    def test_calculate_apertado(self):
        """Test calculating apertado status."""
        role = Role.create(
            team_id=None,
            name="Backend",
            level=RoleLevel.SENIOR,
            base_capacity=5,
        )

        # tasks_per_person = 6 / 1 = 6.0
        # baseline = 5
        # 6.0 > 5.0 and 6.0 <= 6.5 (5*1.3) -> apertado
        health = WorkloadCalculator.calculate_health(
            role=role,
            active_tasks=6,
            users_count=1,
            baseline=5.0,
        )

        assert health.status == "apertado"

    def test_calculate_impossivel(self):
        """Test calculating impossivel status."""
        role = Role.create(
            team_id=None,
            name="Backend",
            level=RoleLevel.SENIOR,
            base_capacity=5,
        )

        # tasks_per_person = 7 / 1 = 7.0
        # baseline = 5
        # 7.0 > 6.5 (5*1.3) -> impossivel
        health = WorkloadCalculator.calculate_health(
            role=role,
            active_tasks=7,
            users_count=1,
            baseline=5.0,
        )

        assert health.status == "impossivel"

    def test_calculate_no_users(self):
        """Test calculating with no users."""
        role = Role.create(
            team_id=None,
            name="Backend",
            level=RoleLevel.SENIOR,
            base_capacity=5,
        )

        health = WorkloadCalculator.calculate_health(
            role=role,
            active_tasks=10,
            users_count=0,
            baseline=5.0,
        )

        assert health.status == "no_users"
        assert health.tasks_per_person == 0.0
