"""UC-054: Get Employee Workload use case."""
from app.application.dtos.task_dtos import WorkloadOutput
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import TaskStatus
from app.domain.models.value_objects import ProjectId, UserId
from app.domain.services.workload_calculator import (
    calculate_capacity,
    calculate_workload_score,
    calculate_workload_status,
)


class GetEmployeeWorkloadUseCase:
    """Use case for computing employee workload (UC-054)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, project_id: ProjectId, user_id: UserId) -> WorkloadOutput:
        """Compute workload for a project member."""
        with self.uow:
            member = self.uow.project_members.find_by_project_and_user(project_id, user_id)
            if member is None:
                raise BusinessRuleViolation("Member not found", code="member_not_found")

            tasks = self.uow.tasks.list_by_project(project_id)
            doing_tasks = [
                task for task in tasks
                if task.assigned_to == user_id and task.status == TaskStatus.DOING
            ]
            workload_score = calculate_workload_score(doing_tasks)
            capacity = calculate_capacity(member.base_capacity, member.level)
            status = calculate_workload_status(workload_score, capacity)
            return WorkloadOutput(
                workload_score=workload_score,
                capacity=capacity,
                status=status,
            )
