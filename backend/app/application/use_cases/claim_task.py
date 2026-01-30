"""UC-006: Claim Task use case (v3.0 with BR-PROJ-002, BR-TASK-002, BR-ASSIGN-003)."""
from datetime import datetime, UTC
from typing import Optional
from uuid import UUID

from app.domain.models.note import Note
from app.domain.models.task_assignment_history import TaskAssignmentHistory
from app.domain.services.workload_calculator import WorkloadCalculator
from app.application.ports.task_repository import TaskRepository
from app.application.ports.user_repository import UserRepository
from app.application.ports.role_repository import RoleRepository
from app.application.ports.project_repository import ProjectRepository
from app.application.ports.note_repository import NoteRepository
from app.application.ports.project_member_repository import ProjectMemberRepository
from app.application.ports.task_assignment_history_repository import TaskAssignmentHistoryRepository
from app.application.ports.event_bus import EventBus
from app.application.events.domain_events import TaskAssigned
from app.domain.exceptions import BusinessRuleViolation


class ClaimTaskUseCase:
    """Use case for claiming a task (UC-006, v3.0)."""

    def __init__(
        self,
        task_repository: TaskRepository,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        project_repository: ProjectRepository,
        note_repository: NoteRepository,
        event_bus: EventBus,
        project_member_repository: Optional[ProjectMemberRepository] = None,
        task_assignment_history_repository: Optional[TaskAssignmentHistoryRepository] = None,
        base_capacity: int = 10,  # Default base capacity for workload calculations
    ):
        self.task_repository = task_repository
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.project_repository = project_repository
        self.note_repository = note_repository
        self.event_bus = event_bus
        self.project_member_repository = project_member_repository
        self.task_assignment_history_repository = task_assignment_history_repository
        self.base_capacity = base_capacity

    def execute(
        self,
        task_id: UUID,
        user_id: UUID,
    ) -> None:
        """
        Claim a task.

        Flow:
        1. Load task and user
        2. Get user's project membership (v3.0)
        3. BR-PROJ-002: Reject if user is a manager
        4. BR-TASK-002: Reject if difficulty is not set
        5. BR-ASSIGN-003: Calculate projected workload, reject if IMPOSSIBLE
        6. Get user's roles in the team
        7. Validate user has required role (BR-002)
        8. Claim task (domain method handles validation)
        9. Record TaskAssignmentHistory
        10. Emit TaskAssigned event
        11. Create note
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

        # v3.0: Check project membership and role
        if self.project_member_repository is not None:
            project_member = self.project_member_repository.find_by_project_and_user(
                project_id=task.project_id,
                user_id=user_id,
            )

            if project_member is not None:
                # BR-PROJ-002: Managers cannot claim tasks
                if project_member.is_manager():
                    raise BusinessRuleViolation(
                        "Managers cannot claim tasks",
                        code="manager_cannot_claim"
                    )

                # BR-TASK-002: Difficulty must be set for selection
                if not task.can_be_selected():
                    raise BusinessRuleViolation(
                        "Task difficulty must be set before it can be claimed",
                        code="difficulty_not_set"
                    )

                # BR-ASSIGN-003: Check workload would not become impossible
                current_tasks = self.task_repository.find_by_user_id(user_id)
                would_be_impossible = WorkloadCalculator.would_be_impossible(
                    current_tasks=current_tasks,
                    new_task=task,
                    base_capacity=self.base_capacity,
                    level=project_member.level,
                )

                if would_be_impossible:
                    raise BusinessRuleViolation(
                        "Cannot claim task: workload would become impossible",
                        code="workload_would_be_impossible"
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

        # v3.0: Record assignment history
        if self.task_assignment_history_repository is not None:
            history = TaskAssignmentHistory.record_started(
                task_id=task.id,
                user_id=user_id,
            )
            self.task_assignment_history_repository.save(history)

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
