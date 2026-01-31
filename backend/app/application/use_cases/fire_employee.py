"""UC-051: Fire Employee use case."""
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import AbandonmentType, TaskStatus
from app.domain.models.task_abandonment import TaskAbandonment
from app.domain.models.value_objects import ProjectId, UserId


class FireEmployeeUseCase:
    """Use case for firing an employee (UC-051)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, project_id: ProjectId, user_id: UserId) -> None:
        """Fire an employee and unassign their tasks."""
        with self.uow:
            member = self.uow.project_members.find_by_project_and_user(project_id, user_id)
            if member is None:
                raise BusinessRuleViolation("Member not found", code="member_not_found")

            tasks = self.uow.tasks.list_by_project(project_id)
            for task in tasks:
                if task.assigned_to != user_id:
                    continue
                task.assigned_to = None
                if task.status == TaskStatus.DOING:
                    task.transition_to(TaskStatus.TODO)
                self.uow.tasks.save(task)

                abandonment = TaskAbandonment.create(
                    task_id=task.id,
                    user_id=user_id,
                    abandonment_type=AbandonmentType.FIRED_FROM_PROJECT,
                    note="employee_fired",
                )
                self.uow.task_abandonments.save(abandonment)

            self.uow.commit()
