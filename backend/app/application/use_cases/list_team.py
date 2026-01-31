"""UC-053: List Team use case."""
from typing import List

from app.application.dtos.project_dtos import ProjectMemberOutput
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.models.value_objects import ProjectId


class ListTeamUseCase:
    """Use case for listing team members (UC-053)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, project_id: ProjectId) -> List[ProjectMemberOutput]:
        """List members of a project."""
        with self.uow:
            members = self.uow.project_members.list_by_project(project_id)
            return [ProjectMemberOutput.from_domain(member) for member in members]
