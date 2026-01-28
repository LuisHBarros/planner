"""UC-005: Create Task use case."""
from datetime import datetime, UTC

from app.domain.models.task import Task
from app.domain.models.note import Note
from app.domain.services.ranking import calculate_rank_index
from app.application.ports.unit_of_work import UnitOfWork
from app.application.ports.event_bus import EventBus
from app.application.events.domain_events import TaskCreated
from app.application.use_cases.dtos import CreateTaskInputDTO
from app.domain.exceptions import BusinessRuleViolation


class CreateTaskUseCase:
    """Use case for creating a task (UC-005)."""

    def __init__(
        self,
        uow: UnitOfWork,
        event_bus: EventBus,
    ):
        self.uow = uow
        self.event_bus = event_bus

    def execute(
        self,
        input_dto: CreateTaskInputDTO,
    ) -> Task:
        """
        Create a new task.
        
        Flow:
        1. Validate project and role exist
        2. Validate role belongs to project's team (BR-001)
        3. Calculate rank_index
        4. Create task
        5. Emit TaskCreated event
        6. Create system note
        7. Return task details
        """
        with self.uow:
            # Load dependencies
            project = self.uow.projects.find_by_id(input_dto.project_id)
            if project is None:
                raise BusinessRuleViolation(
                    f"Project with id {input_dto.project_id} not found",
                    code="project_not_found",
                )

            role = self.uow.roles.find_by_id(input_dto.role_responsible_id)
            if role is None:
                raise BusinessRuleViolation(
                    f"Role with id {input_dto.role_responsible_id} not found",
                    code="role_not_found",
                )

            # BR-001: Role must belong to project's team
            if role.team_id != project.team_id:
                raise BusinessRuleViolation(
                    "Role must belong to project's team",
                    code="role_not_in_team",
                )

            # Calculate rank_index (BR-011)
            existing_tasks = self.uow.tasks.find_by_project_id(input_dto.project_id)
            rank_index = calculate_rank_index(len(existing_tasks), existing_tasks)

            # Create task (BR-005: defaults to todo)
            task = Task.create(
                project_id=input_dto.project_id,
                title=input_dto.title,
                description=input_dto.description,
                role_responsible_id=input_dto.role_responsible_id,
                priority=input_dto.priority,
                due_date=input_dto.due_date,
                rank_index=rank_index,
            )

            # Save
            self.uow.tasks.save(task)

            # Emit event
            self.event_bus.emit(
                TaskCreated(
                    task_id=task.id,
                    project_id=input_dto.project_id,
                    role_id=input_dto.role_responsible_id,
                    title=input_dto.title,
                    created_by=input_dto.created_by or task.id,  # Fallback if not provided
                    timestamp=datetime.now(UTC),
                )
            )

            # Create system note
            if input_dto.created_by:
                # Note: In real implementation, we'd get user name from user repository
                note = Note.create_system_note(
                    task_id=task.id,
                    content=f"Task created by user {input_dto.created_by}",
                )
                self.uow.notes.save(note)

            return task
