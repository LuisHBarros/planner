"""UC-063: View Schedule History use case."""
from typing import List, Tuple

from app.application.dtos.schedule_dtos import (
    ProjectScheduleHistoryOutput,
    TaskScheduleHistoryOutput,
)
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.models.value_objects import ProjectId, TaskId


class ViewScheduleHistoryUseCase:
    """Use case for viewing schedule history (UC-063)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(
        self,
        project_id: ProjectId | None = None,
        task_id: TaskId | None = None,
    ) -> Tuple[List[ProjectScheduleHistoryOutput], List[TaskScheduleHistoryOutput]]:
        """View schedule history for a project or task."""
        with self.uow:
            project_history = []
            task_history = []
            if project_id is not None:
                project_history = [
                    ProjectScheduleHistoryOutput.from_domain(item)
                    for item in self.uow.schedule_history.list_project_history(project_id)
                ]
            if task_id is not None:
                task_history = [
                    TaskScheduleHistoryOutput.from_domain(item)
                    for item in self.uow.schedule_history.list_task_history(task_id)
                ]
            return project_history, task_history
