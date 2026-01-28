"""UC-005: Create Task use case."""
from datetime import datetime, UTC
from uuid import UUID
from typing import Optional

from app.domain.models.task import Task
from app.domain.models.note import Note
from app.domain.models.enums import TaskPriority
from app.domain.services.ranking import calculate_rank_index
from app.application.ports.task_repository import TaskRepository
from app.application.ports.project_repository import ProjectRepository
from app.application.ports.role_repository import RoleRepository
from app.application.ports.note_repository import NoteRepository
from app.application.ports.event_bus import EventBus
from app.application.events.domain_events import TaskCreated
from app.domain.exceptions import BusinessRuleViolation


class CreateTaskUseCase:
    """Use case for creating a task (UC-005)."""
    
    def __init__(
        self,
        task_repository: TaskRepository,
        project_repository: ProjectRepository,
        role_repository: RoleRepository,
        note_repository: NoteRepository,
        event_bus: EventBus,
    ):
        self.task_repository = task_repository
        self.project_repository = project_repository
        self.role_repository = role_repository
        self.note_repository = note_repository
        self.event_bus = event_bus
    
    def execute(
        self,
        project_id: UUID,
        title: str,
        description: str,
        role_responsible_id: UUID,
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: Optional[datetime] = None,
        created_by: UUID = None,
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
        # Load dependencies
        project = self.project_repository.find_by_id(project_id)
        if project is None:
            raise BusinessRuleViolation(
                f"Project with id {project_id} not found",
                code="project_not_found"
            )
        
        role = self.role_repository.find_by_id(role_responsible_id)
        if role is None:
            raise BusinessRuleViolation(
                f"Role with id {role_responsible_id} not found",
                code="role_not_found"
            )
        
        # BR-001: Role must belong to project's team
        if role.team_id != project.team_id:
            raise BusinessRuleViolation(
                "Role must belong to project's team",
                code="role_not_in_team"
            )
        
        # Calculate rank_index (BR-011)
        existing_tasks = self.task_repository.find_by_project_id(project_id)
        rank_index = calculate_rank_index(len(existing_tasks), existing_tasks)
        
        # Create task (BR-005: defaults to todo)
        task = Task.create(
            project_id=project_id,
            title=title,
            description=description,
            role_responsible_id=role_responsible_id,
            priority=priority,
            due_date=due_date,
            rank_index=rank_index,
        )
        
        # Save
        self.task_repository.save(task)
        
        # Emit event
        self.event_bus.emit(
            TaskCreated(
                task_id=task.id,
                project_id=project_id,
                role_id=role_responsible_id,
                title=title,
                created_by=created_by or task.id,  # Fallback if not provided
                timestamp=datetime.now(UTC),
            )
        )
        
        # Create system note
        if created_by:
            # Note: In real implementation, we'd get user name from user repository
            note = Note.create_system_note(
                task_id=task.id,
                content=f"Task created by user {created_by}",
            )
            self.note_repository.save(note)
        
        return task
