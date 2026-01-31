"""UC-040: Select Task use case."""
from app.application.dtos.task_dtos import SelectTaskInput, TaskOutput
from app.application.events.domain_events import TaskAssigned
from app.application.ports.event_bus import EventBus
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import TaskStatus
from app.domain.models.task_assignment_history import TaskAssignmentHistory
from app.domain.models.value_objects import UtcDateTime
from app.domain.services.workload_calculator import would_be_impossible


class SelectTaskUseCase:
    """Use case for selecting a task (UC-040)."""

    def __init__(self, uow: UnitOfWork, event_bus: EventBus):
        self.uow = uow
        self.event_bus = event_bus

    def execute(self, input_dto: SelectTaskInput) -> TaskOutput:
        """Select a task for a user."""
        with self.uow:
            task = self.uow.tasks.find_by_id(input_dto.task_id)
            if task is None:
                raise BusinessRuleViolation("Task not found", code="task_not_found")

            member = self.uow.project_members.find_by_project_and_user(
                task.project_id,
                input_dto.user_id,
            )
            if member is None:
                raise BusinessRuleViolation("Member not found", code="member_not_found")

            if member.is_manager:
                raise BusinessRuleViolation(
                    "Managers cannot claim tasks",
                    code="manager_cannot_claim",
                )

            if task.difficulty is None:
                raise BusinessRuleViolation(
                    "Task difficulty must be set before selection",
                    code="difficulty_not_set",
                )

            project_tasks = self.uow.tasks.list_by_project(task.project_id)
            current_tasks = [
                item for item in project_tasks
                if item.assigned_to == input_dto.user_id
                and item.status == TaskStatus.DOING
            ]
            if would_be_impossible(
                current_tasks,
                task,
                base_capacity=member.base_capacity,
                level=member.level,
            ):
                raise BusinessRuleViolation(
                    "Workload would become impossible",
                    code="workload_impossible",
                )

            task.assigned_to = input_dto.user_id
            if task.actual_start_date is None:
                task.actual_start_date = UtcDateTime.now()
            task.transition_to(TaskStatus.DOING)
            self.uow.tasks.save(task)

            history = TaskAssignmentHistory.create(
                task_id=task.id,
                user_id=input_dto.user_id,
                assignment_reason="select_task",
            )
            self.uow.task_assignment_history.save(history)

            self.uow.commit()

            self.event_bus.emit(TaskAssigned(task_id=task.id, user_id=input_dto.user_id))
            return TaskOutput.from_domain(task)
