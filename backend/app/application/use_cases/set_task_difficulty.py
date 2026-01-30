"""UC: Set Task Difficulty use case (v3.0)."""
from datetime import datetime, UTC
from typing import Optional
from uuid import UUID

from app.domain.models.note import Note
from app.domain.models.task import Task
from app.application.ports.task_repository import TaskRepository
from app.application.ports.note_repository import NoteRepository
from app.application.ports.project_member_repository import ProjectMemberRepository
from app.application.ports.event_bus import EventBus
from app.application.events.domain_events import DifficultySet
from app.domain.exceptions import BusinessRuleViolation


class SetTaskDifficultyUseCase:
    """
    Use case for setting task difficulty (v3.0 BR-TASK-002).

    Only managers can set task difficulty. Difficulty must be between 1-10.
    Tasks cannot be claimed/selected until difficulty is set.
    """

    def __init__(
        self,
        task_repository: TaskRepository,
        note_repository: NoteRepository,
        project_member_repository: ProjectMemberRepository,
        event_bus: EventBus,
    ):
        self.task_repository = task_repository
        self.note_repository = note_repository
        self.project_member_repository = project_member_repository
        self.event_bus = event_bus

    def execute(
        self,
        task_id: UUID,
        difficulty: int,
        set_by_user_id: UUID,
    ) -> Task:
        """
        Set task difficulty.

        Args:
            task_id: The task to set difficulty for
            difficulty: The difficulty value (1-10)
            set_by_user_id: The user setting the difficulty (must be a manager)

        Returns:
            The updated task
        """
        # Load task
        task = self.task_repository.find_by_id(task_id)
        if task is None:
            raise BusinessRuleViolation(
                f"Task with id {task_id} not found",
                code="task_not_found"
            )

        # Verify user is a manager in the project
        project_member = self.project_member_repository.find_by_project_and_user(
            project_id=task.project_id,
            user_id=set_by_user_id,
        )

        if project_member is None:
            raise BusinessRuleViolation(
                "User is not a member of this project",
                code="not_project_member"
            )

        if not project_member.is_manager():
            raise BusinessRuleViolation(
                "Only managers can set task difficulty",
                code="not_manager"
            )

        old_difficulty = task.difficulty

        # Set difficulty (domain method validates range)
        task.set_difficulty(difficulty)

        # Save task
        self.task_repository.save(task)

        # Emit event
        self.event_bus.emit(
            DifficultySet(
                task_id=task.id,
                difficulty=difficulty,
                set_by_user_id=set_by_user_id,
                timestamp=datetime.now(UTC),
            )
        )

        # Create note
        if old_difficulty is None:
            note_content = f"Difficulty set to {difficulty}"
        else:
            note_content = f"Difficulty changed from {old_difficulty} to {difficulty}"

        note = Note.create_system_note(
            task_id=task.id,
            content=note_content,
        )
        self.note_repository.save(note)

        return task
