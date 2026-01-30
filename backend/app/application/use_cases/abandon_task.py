"""UC: Abandon Task use case (v3.0)."""
from datetime import datetime, UTC
from typing import Optional, List
from uuid import UUID

from app.domain.models.note import Note
from app.domain.models.task import Task
from app.domain.models.task_abandonment import TaskAbandonment
from app.domain.models.task_assignment_history import TaskAssignmentHistory
from app.domain.models.enums import AbandonmentType, TaskStatus
from app.application.ports.task_repository import TaskRepository
from app.application.ports.note_repository import NoteRepository
from app.application.ports.project_member_repository import ProjectMemberRepository
from app.application.ports.task_abandonment_repository import TaskAbandonmentRepository
from app.application.ports.task_assignment_history_repository import TaskAssignmentHistoryRepository
from app.application.ports.event_bus import EventBus
from app.application.events.domain_events import TaskAbandoned
from app.domain.exceptions import BusinessRuleViolation


class AbandonTaskUseCase:
    """
    Use case for abandoning a task (v3.0).

    Handles multiple abandonment scenarios:
    - VOLUNTARY: Employee abandons their own task
    - FIRED_FROM_TASK: Manager removes employee from task
    - FIRED_FROM_PROJECT: Manager fires employee (abandons all their tasks)
    - RESIGNED: Employee resigns (abandons all their tasks)
    """

    def __init__(
        self,
        task_repository: TaskRepository,
        note_repository: NoteRepository,
        project_member_repository: ProjectMemberRepository,
        task_abandonment_repository: TaskAbandonmentRepository,
        task_assignment_history_repository: TaskAssignmentHistoryRepository,
        event_bus: EventBus,
    ):
        self.task_repository = task_repository
        self.note_repository = note_repository
        self.project_member_repository = project_member_repository
        self.task_abandonment_repository = task_abandonment_repository
        self.task_assignment_history_repository = task_assignment_history_repository
        self.event_bus = event_bus

    def execute_voluntary(
        self,
        task_id: UUID,
        user_id: UUID,
        reason: Optional[str] = None,
    ) -> Task:
        """
        Employee voluntarily abandons their own task.

        Args:
            task_id: The task to abandon
            user_id: The user abandoning the task (must be the assigned user)
            reason: Optional reason for abandonment

        Returns:
            The updated task
        """
        task = self._get_task(task_id)

        # Verify user is assigned to this task
        if task.user_responsible_id != user_id:
            raise BusinessRuleViolation(
                "Can only abandon tasks assigned to you",
                code="not_assigned_to_task"
            )

        return self._abandon_task(
            task=task,
            user_id=user_id,
            abandonment_type=AbandonmentType.VOLUNTARY,
            initiated_by_user_id=user_id,
            reason=reason,
        )

    def execute_fired_from_task(
        self,
        task_id: UUID,
        employee_user_id: UUID,
        manager_user_id: UUID,
        reason: Optional[str] = None,
    ) -> Task:
        """
        Manager removes employee from a specific task.

        Args:
            task_id: The task to remove employee from
            employee_user_id: The employee being removed
            manager_user_id: The manager performing the action
            reason: Optional reason for removal

        Returns:
            The updated task
        """
        task = self._get_task(task_id)

        # Verify employee is assigned to this task
        if task.user_responsible_id != employee_user_id:
            raise BusinessRuleViolation(
                "Employee is not assigned to this task",
                code="not_assigned_to_task"
            )

        # Verify manager has authority
        self._verify_manager_authority(task.project_id, manager_user_id)

        return self._abandon_task(
            task=task,
            user_id=employee_user_id,
            abandonment_type=AbandonmentType.FIRED_FROM_TASK,
            initiated_by_user_id=manager_user_id,
            reason=reason,
        )

    def execute_fired_from_project(
        self,
        project_id: UUID,
        employee_user_id: UUID,
        manager_user_id: UUID,
        reason: Optional[str] = None,
    ) -> List[Task]:
        """
        Manager fires employee from project, abandoning all their tasks.

        Args:
            project_id: The project
            employee_user_id: The employee being fired
            manager_user_id: The manager performing the action
            reason: Optional reason for firing

        Returns:
            List of abandoned tasks
        """
        # Verify manager has authority
        self._verify_manager_authority(project_id, manager_user_id)

        # Find all tasks assigned to this employee in the project
        all_user_tasks = self.task_repository.find_by_user_id(employee_user_id)
        project_tasks = [t for t in all_user_tasks if t.project_id == project_id and t.status == TaskStatus.DOING]

        abandoned_tasks = []
        for task in project_tasks:
            abandoned_task = self._abandon_task(
                task=task,
                user_id=employee_user_id,
                abandonment_type=AbandonmentType.FIRED_FROM_PROJECT,
                initiated_by_user_id=manager_user_id,
                reason=reason,
            )
            abandoned_tasks.append(abandoned_task)

        # Deactivate project membership
        project_member = self.project_member_repository.find_by_project_and_user(
            project_id=project_id,
            user_id=employee_user_id,
        )
        if project_member:
            project_member.deactivate()
            self.project_member_repository.save(project_member)

        return abandoned_tasks

    def execute_resigned(
        self,
        project_id: UUID,
        user_id: UUID,
        reason: Optional[str] = None,
    ) -> List[Task]:
        """
        Employee resigns from project, abandoning all their tasks.

        Args:
            project_id: The project
            user_id: The employee resigning
            reason: Optional reason for resignation

        Returns:
            List of abandoned tasks
        """
        # Find all tasks assigned to this user in the project
        all_user_tasks = self.task_repository.find_by_user_id(user_id)
        project_tasks = [t for t in all_user_tasks if t.project_id == project_id and t.status == TaskStatus.DOING]

        abandoned_tasks = []
        for task in project_tasks:
            abandoned_task = self._abandon_task(
                task=task,
                user_id=user_id,
                abandonment_type=AbandonmentType.RESIGNED,
                initiated_by_user_id=user_id,
                reason=reason,
            )
            abandoned_tasks.append(abandoned_task)

        # Deactivate project membership
        project_member = self.project_member_repository.find_by_project_and_user(
            project_id=project_id,
            user_id=user_id,
        )
        if project_member:
            project_member.deactivate()
            self.project_member_repository.save(project_member)

        return abandoned_tasks

    def _get_task(self, task_id: UUID) -> Task:
        """Get task or raise error."""
        task = self.task_repository.find_by_id(task_id)
        if task is None:
            raise BusinessRuleViolation(
                f"Task with id {task_id} not found",
                code="task_not_found"
            )
        return task

    def _verify_manager_authority(self, project_id: UUID, user_id: UUID) -> None:
        """Verify user is a manager in the project."""
        project_member = self.project_member_repository.find_by_project_and_user(
            project_id=project_id,
            user_id=user_id,
        )

        if project_member is None:
            raise BusinessRuleViolation(
                "User is not a member of this project",
                code="not_project_member"
            )

        if not project_member.is_manager():
            raise BusinessRuleViolation(
                "Only managers can perform this action",
                code="not_manager"
            )

    def _abandon_task(
        self,
        task: Task,
        user_id: UUID,
        abandonment_type: AbandonmentType,
        initiated_by_user_id: UUID,
        reason: Optional[str] = None,
    ) -> Task:
        """Common logic for abandoning a task."""
        # Domain method handles status transition
        task.abandon()

        # Save task
        self.task_repository.save(task)

        # Record abandonment
        abandonment = TaskAbandonment.create(
            task_id=task.id,
            user_id=user_id,
            abandonment_type=abandonment_type,
            initiated_by_user_id=initiated_by_user_id,
            reason=reason,
        )
        self.task_abandonment_repository.save(abandonment)

        # Record assignment history
        history = TaskAssignmentHistory.record_abandoned(
            task_id=task.id,
            user_id=user_id,
            abandonment_type=abandonment_type,
        )
        self.task_assignment_history_repository.save(history)

        # Emit event
        self.event_bus.emit(
            TaskAbandoned(
                task_id=task.id,
                user_id=user_id,
                abandonment_type=abandonment_type,
                initiated_by_user_id=initiated_by_user_id,
                timestamp=datetime.now(UTC),
            )
        )

        # Create note
        note_content = f"Task abandoned ({abandonment_type.value})"
        if reason:
            note_content += f": {reason}"
        note = Note.create_system_note(
            task_id=task.id,
            content=note_content,
        )
        self.note_repository.save(note)

        return task
