"""UC-006: Claim Task use case."""
from datetime import datetime, UTC
from uuid import UUID

from app.domain.models.note import Note
from app.application.ports.task_repository import TaskRepository
from app.application.ports.user_repository import UserRepository
from app.application.ports.role_repository import RoleRepository
from app.application.ports.project_repository import ProjectRepository
from app.application.ports.note_repository import NoteRepository
from app.application.ports.event_bus import EventBus
from app.application.events.domain_events import TaskAssigned
from app.domain.exceptions import BusinessRuleViolation


class ClaimTaskUseCase:
    """Use case for claiming a task (UC-006)."""
    
    def __init__(
        self,
        task_repository: TaskRepository,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        project_repository: ProjectRepository,
        note_repository: NoteRepository,
        event_bus: EventBus,
    ):
        self.task_repository = task_repository
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.project_repository = project_repository
        self.note_repository = note_repository
        self.event_bus = event_bus
    
    def execute(
        self,
        task_id: UUID,
        user_id: UUID,
    ) -> None:
        """
        Claim a task.
        
        Flow:
        1. Load task and user
        2. Get user's roles in the team
        3. Validate user has required role (BR-002)
        4. Claim task (domain method handles validation)
        5. Emit TaskAssigned event
        6. Create note
        7. Return updated task
        """
        # Load task
        task = self.task_repository.find_by_id(task_id)
        if task is None:
            raise BusinessRuleViolation(
                f"Task with id {task_id} not found",
                code="task_not_found"
            )
        
        # Load user
        user = self.user_repository.find_by_id(user_id)
        if user is None:
            raise BusinessRuleViolation(
                f"User with id {user_id} not found",
                code="user_not_found"
            )
        
        # Get project to find team_id
        project = self.project_repository.find_by_id(task.project_id)
        if project is None:
            raise BusinessRuleViolation(
                f"Project with id {task.project_id} not found",
                code="project_not_found"
            )
        
        # Get user's roles in the team
        user_roles = self.role_repository.find_by_user_and_team(
            user_id=user_id,
            team_id=project.team_id,
        )
        user_role_ids = [role.id for role in user_roles]
        
        # Claim task (domain method validates BR-002)
        task.claim(user, user_role_ids)
        
        # Save
        self.task_repository.save(task)
        
        # Emit event
        self.event_bus.emit(
            TaskAssigned(
                task_id=task.id,
                user_id=user_id,
                timestamp=datetime.now(UTC),
            )
        )
        
        # Create note
        note = Note.create_system_note(
            task_id=task.id,
            content=f"Task claimed by user {user_id}",
        )
        self.note_repository.save(note)
