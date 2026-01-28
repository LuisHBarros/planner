"""UC: Remove Task Dependency use case."""
from datetime import datetime, UTC
from typing import Optional
from uuid import UUID

from app.domain.models.task import Task
from app.domain.models.task_dependency import TaskDependency
from app.domain.models.note import Note
from app.domain.models.enums import DependencyType, TaskStatus
from app.application.ports.task_repository import TaskRepository
from app.application.ports.task_dependency_repository import TaskDependencyRepository
from app.application.ports.note_repository import NoteRepository
from app.application.ports.project_repository import ProjectRepository
try:
    from app.application.ports.team_member_repository import TeamMemberRepository
except ImportError:
    TeamMemberRepository = None  # type: ignore
from app.application.ports.event_bus import EventBus
from app.application.events.domain_events import TaskUnblocked
from app.domain.exceptions import BusinessRuleViolation


class RemoveTaskDependencyUseCase:
    """Use case for removing a task dependency."""

    def __init__(
        self,
        task_repository: TaskRepository,
        task_dependency_repository: TaskDependencyRepository,
        project_repository: ProjectRepository,
        note_repository: NoteRepository,
        team_member_repository: Optional[TeamMemberRepository] = None,
        event_bus: Optional[EventBus] = None,
    ):
        self.task_repository = task_repository
        self.task_dependency_repository = task_dependency_repository
        self.project_repository = project_repository
        self.note_repository = note_repository
        self.team_member_repository = team_member_repository
        self.event_bus = event_bus

    def _check_manager_permission(
        self, actor_user_id: Optional[UUID], project_id: UUID
    ) -> None:
        """
        Check if actor is a manager for the project's team.

        If team_member_repository is None or actor_user_id is None, skip check (MVP mode).
        """
        if self.team_member_repository is None or actor_user_id is None:
            # MVP: skip permission check if not available
            return

        project = self.project_repository.find_by_id(project_id)
        if project is None:
            return

        # Check if user is manager in the team
        memberships = self.team_member_repository.find_by_user_id(actor_user_id)
        for membership in memberships:
            if membership.team_id == project.team_id:
                try:
                    from app.domain.models.enums import TeamMemberRole

                    if membership.role == TeamMemberRole.MANAGER:
                        return
                except ImportError:
                    # TeamMemberRole not available - skip permission check
                    return

        raise BusinessRuleViolation(
            "Only team managers can remove dependencies",
            code="permission_denied",
        )

    def execute(
        self,
        task_id: UUID,
        dependency_id: UUID,
        actor_user_id: Optional[UUID] = None,
    ) -> None:
        """
        Remove a task dependency.

        Flow:
        1. Load dependency and verify it belongs to task_id
        2. Check manager permission (if available)
        3. If dependency was BLOCKS type:
           - Check remaining blocking dependencies
           - If none remain and task is BLOCKED, unblock it
        4. Delete dependency
        5. Create system note
        6. Emit TaskUnblocked event if task was unblocked
        """
        # Load dependency
        dependency = self.task_dependency_repository.find_by_id(dependency_id)
        if dependency is None:
            raise BusinessRuleViolation(
                f"Dependency with id {dependency_id} not found",
                code="dependency_not_found",
            )

        # Verify dependency belongs to task_id
        if dependency.task_id != task_id:
            raise BusinessRuleViolation(
                f"Dependency does not belong to task {task_id}",
                code="dependency_mismatch",
            )

        # Load task
        task = self.task_repository.find_by_id(task_id)
        if task is None:
            raise BusinessRuleViolation(
                f"Task with id {task_id} not found",
                code="task_not_found",
            )

        # Check permission
        self._check_manager_permission(actor_user_id, task.project_id)

        # If removing a BLOCKS dependency, check if we should unblock the task
        was_blocking = dependency.dependency_type == DependencyType.BLOCKS
        should_unblock = False

        if was_blocking:
            # Get all remaining dependencies for this task
            remaining_deps = self.task_dependency_repository.find_by_task_id(task_id)
            remaining_blocking_deps = [
                d
                for d in remaining_deps
                if d.id != dependency_id and d.dependency_type == DependencyType.BLOCKS
            ]

            # Check if any remaining blockers are not done
            has_active_blockers = False
            for dep in remaining_blocking_deps:
                blocker_task = self.task_repository.find_by_id(dep.depends_on_task_id)
                if blocker_task and blocker_task.status != TaskStatus.DONE:
                    has_active_blockers = True
                    break

            # Unblock if: task is BLOCKED, no remaining blocking deps, or all blockers are done
            if (
                task.status == TaskStatus.BLOCKED
                and not has_active_blockers
                and len(remaining_blocking_deps) == 0
            ):
                should_unblock = True

        # Delete dependency
        self.task_dependency_repository.delete(dependency_id)

        # Unblock task if needed
        if should_unblock:
            task.unblock()
            self.task_repository.save(task)

            if self.event_bus:
                self.event_bus.emit(
                    TaskUnblocked(
                        task_id=task.id,
                        timestamp=datetime.now(UTC),
                        user_id=actor_user_id,
                    )
                )

        # Create system note
        note = Note.create_system_note(
            task_id=task_id,
            content=f"Dependency removed: Task #{dependency.depends_on_task_id}",
        )
        self.note_repository.save(note)
