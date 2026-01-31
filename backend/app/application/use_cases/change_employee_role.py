"""UC-070: Change Employee Role use case."""
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.value_objects import ProjectId, RoleId, UserId


class ChangeEmployeeRoleUseCase:
    """Use case for changing an employee role (UC-070)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, project_id: ProjectId, user_id: UserId, role_id: RoleId | None) -> None:
        """Change an employee role assignment."""
        with self.uow:
            member = self.uow.project_members.find_by_project_and_user(project_id, user_id)
            if member is None:
                raise BusinessRuleViolation("Member not found", code="member_not_found")
            member.role_id = role_id
            self.uow.project_members.save(member)
            self.uow.commit()
