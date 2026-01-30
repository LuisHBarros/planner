"""Workload calculator service (v3.0 BR-WORK-001/002/003)."""
from typing import List, Optional

from app.domain.models.enums import RoleLevel, WorkloadStatus, TaskStatus
from app.domain.models.task import Task
from app.domain.models.role import Role


# Level multipliers for capacity calculation (BR-WORK-001)
LEVEL_MULTIPLIERS = {
    RoleLevel.JUNIOR: 0.6,
    RoleLevel.MID: 1.0,
    RoleLevel.SENIOR: 1.3,
    RoleLevel.SPECIALIST: 1.2,
    RoleLevel.LEAD: 1.1,
}

# Workload status thresholds (BR-WORK-002)
# Based on ratio of workload_score / capacity
WORKLOAD_THRESHOLDS = {
    "IMPOSSIBLE": 1.5,  # ratio > 1.5
    "TIGHT": 1.2,  # ratio > 1.2
    "HEALTHY": 0.7,  # ratio > 0.7
    "RELAXED": 0.3,  # ratio > 0.3
    # IDLE: ratio <= 0.3
}


class WorkloadHealth:
    """Workload health status (legacy compatibility)."""

    def __init__(
        self,
        status: str,
        tasks_per_person: float,
        baseline: float,
    ):
        self.status = status
        self.tasks_per_person = tasks_per_person
        self.baseline = baseline


class WorkloadResult:
    """Result of workload calculation (v3.0)."""

    def __init__(
        self,
        status: WorkloadStatus,
        score: int,
        capacity: float,
        ratio: float,
    ):
        self.status = status
        self.score = score
        self.capacity = capacity
        self.ratio = ratio


class WorkloadCalculator:
    """Domain service for workload calculations (v3.0 BR-WORK)."""

    @staticmethod
    def get_level_multiplier(level: RoleLevel) -> float:
        """Get the capacity multiplier for a role level (BR-WORK-001)."""
        return LEVEL_MULTIPLIERS.get(level, 1.0)

    @staticmethod
    def calculate_capacity(base_capacity: int, level: RoleLevel) -> float:
        """
        Calculate effective capacity based on level (BR-WORK-001).

        Args:
            base_capacity: The base capacity value
            level: The seniority level

        Returns:
            Effective capacity (base * level multiplier)
        """
        multiplier = WorkloadCalculator.get_level_multiplier(level)
        return base_capacity * multiplier

    @staticmethod
    def calculate_workload_score(tasks: List[Task]) -> int:
        """
        Calculate workload score from active tasks (BR-WORK-002).

        The score is the sum of difficulty for all tasks in DOING status.

        Args:
            tasks: List of tasks assigned to the user

        Returns:
            Sum of difficulty values for DOING tasks
        """
        total = 0
        for task in tasks:
            if task.status == TaskStatus.DOING:
                # Use difficulty if set, otherwise count as 1
                total += task.difficulty if task.difficulty is not None else 1
        return total

    @staticmethod
    def calculate_status(score: int, capacity: float) -> WorkloadStatus:
        """
        Calculate workload status from score and capacity (BR-WORK-002).

        Thresholds:
        - ratio > 1.5 -> IMPOSSIBLE
        - ratio > 1.2 -> TIGHT
        - ratio > 0.7 -> HEALTHY
        - ratio > 0.3 -> RELAXED
        - ratio <= 0.3 -> IDLE

        Args:
            score: Current workload score
            capacity: Effective capacity

        Returns:
            WorkloadStatus enum value
        """
        if capacity <= 0:
            # No capacity means any work is impossible
            return WorkloadStatus.IMPOSSIBLE if score > 0 else WorkloadStatus.IDLE

        ratio = score / capacity

        if ratio > WORKLOAD_THRESHOLDS["IMPOSSIBLE"]:
            return WorkloadStatus.IMPOSSIBLE
        elif ratio > WORKLOAD_THRESHOLDS["TIGHT"]:
            return WorkloadStatus.TIGHT
        elif ratio > WORKLOAD_THRESHOLDS["HEALTHY"]:
            return WorkloadStatus.HEALTHY
        elif ratio > WORKLOAD_THRESHOLDS["RELAXED"]:
            return WorkloadStatus.RELAXED
        else:
            return WorkloadStatus.IDLE

    @staticmethod
    def calculate_workload(
        tasks: List[Task],
        base_capacity: int,
        level: RoleLevel,
    ) -> WorkloadResult:
        """
        Calculate complete workload result (v3.0).

        Args:
            tasks: List of tasks assigned to the user
            base_capacity: The base capacity value
            level: The seniority level

        Returns:
            WorkloadResult with status, score, capacity, and ratio
        """
        score = WorkloadCalculator.calculate_workload_score(tasks)
        capacity = WorkloadCalculator.calculate_capacity(base_capacity, level)

        if capacity <= 0:
            ratio = float("inf") if score > 0 else 0.0
        else:
            ratio = score / capacity

        status = WorkloadCalculator.calculate_status(score, capacity)

        return WorkloadResult(
            status=status,
            score=score,
            capacity=capacity,
            ratio=ratio,
        )

    @staticmethod
    def simulate_assignment(
        current_tasks: List[Task],
        new_task: Task,
        base_capacity: int,
        level: RoleLevel,
    ) -> WorkloadResult:
        """
        Simulate workload after assigning a new task (BR-ASSIGN-003).

        Projects what the workload would be if the new task were assigned.
        Used to reject assignments that would make workload IMPOSSIBLE.

        Args:
            current_tasks: Current tasks assigned to the user
            new_task: The task being considered for assignment
            base_capacity: The base capacity value
            level: The seniority level

        Returns:
            WorkloadResult representing projected workload after assignment
        """
        # Calculate current score
        current_score = WorkloadCalculator.calculate_workload_score(current_tasks)

        # Add the new task's difficulty (assuming it would be DOING)
        new_task_difficulty = new_task.difficulty if new_task.difficulty is not None else 1
        projected_score = current_score + new_task_difficulty

        capacity = WorkloadCalculator.calculate_capacity(base_capacity, level)

        if capacity <= 0:
            ratio = float("inf") if projected_score > 0 else 0.0
        else:
            ratio = projected_score / capacity

        status = WorkloadCalculator.calculate_status(projected_score, capacity)

        return WorkloadResult(
            status=status,
            score=projected_score,
            capacity=capacity,
            ratio=ratio,
        )

    @staticmethod
    def would_be_impossible(
        current_tasks: List[Task],
        new_task: Task,
        base_capacity: int,
        level: RoleLevel,
    ) -> bool:
        """
        Check if assigning a task would make workload impossible (BR-ASSIGN-003).

        Args:
            current_tasks: Current tasks assigned to the user
            new_task: The task being considered for assignment
            base_capacity: The base capacity value
            level: The seniority level

        Returns:
            True if assignment would result in IMPOSSIBLE workload
        """
        result = WorkloadCalculator.simulate_assignment(
            current_tasks, new_task, base_capacity, level
        )
        return result.status == WorkloadStatus.IMPOSSIBLE

    # Legacy method for backward compatibility with existing code
    @staticmethod
    def calculate_health(
        role: Role,
        active_tasks: int,
        users_count: int,
        baseline: float,
    ) -> WorkloadHealth:
        """
        Calculate workload health for a role (legacy BR-010 compatibility).

        Health levels (BR-010):
        - tasks_per_person < baseline * 0.8  -> tranquilo (green)
        - tasks_per_person <= baseline       -> saudavel (yellow)
        - tasks_per_person <= baseline * 1.3 -> apertado (orange)
        - tasks_per_person > baseline * 1.3  -> impossivel (red)

        Args:
            role: The role being analyzed
            active_tasks: Number of active tasks
            users_count: Number of users with this role
            baseline: Baseline capacity value

        Returns:
            WorkloadHealth with status and metrics
        """
        if users_count == 0:
            return WorkloadHealth(
                status="no_users",
                tasks_per_person=0.0,
                baseline=baseline,
            )

        tasks_per_person = active_tasks / users_count

        if tasks_per_person < baseline * 0.8:
            status = "tranquilo"
        elif tasks_per_person <= baseline:
            status = "saudavel"
        elif tasks_per_person <= baseline * 1.3:
            status = "apertado"
        else:
            status = "impossivel"

        return WorkloadHealth(
            status=status,
            tasks_per_person=tasks_per_person,
            baseline=baseline,
        )
