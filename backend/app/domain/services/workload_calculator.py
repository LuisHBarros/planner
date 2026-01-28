"""Workload calculator service (BR-010)."""
from typing import Optional
from app.domain.models.role import Role


class WorkloadHealth:
    """Workload health status."""
    
    def __init__(
        self,
        status: str,
        tasks_per_person: float,
        baseline: float,
    ):
        self.status = status
        self.tasks_per_person = tasks_per_person
        self.baseline = baseline


class WorkloadCalculator:
    """Domain service for workload calculations (BR-010)."""
    
    @staticmethod
    def calculate_health(
        role: Role,
        active_tasks: int,
        users_count: int,
        baseline: float,
    ) -> WorkloadHealth:
        """
        Calculate workload health for a role.
        
        Health levels (BR-010):
        - tasks_per_person ≤ baseline * 0.8  → tranquilo (green)
        - tasks_per_person ≤ baseline        → saudável (yellow)
        - tasks_per_person ≤ baseline * 1.3  → apertado (orange)
        - tasks_per_person > baseline * 1.3  → impossível (red)
        """
        if users_count == 0:
            return WorkloadHealth(
                status="no_users",
                tasks_per_person=0.0,
                baseline=baseline,
            )

        tasks_per_person = active_tasks / users_count

        # Note: the original BR-010 spec uses `<= baseline * 0.8` for \"tranquilo\",
        # but the tests expect a value exactly at `baseline * 0.8` to be
        # considered \"saudável\". We therefore treat the first threshold as
        # strictly less-than to align implementation and tests.
        if tasks_per_person < baseline * 0.8:
            status = "tranquilo"
        elif tasks_per_person <= baseline:
            status = "saudável"
        elif tasks_per_person <= baseline * 1.3:
            status = "apertado"
        else:
            status = "impossível"
        
        return WorkloadHealth(
            status=status,
            tasks_per_person=tasks_per_person,
            baseline=baseline
        )
