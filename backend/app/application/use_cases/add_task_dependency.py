"""UC-010: Add Task Dependency use case."""
from datetime import datetime, UTC
from uuid import UUID

from app.domain.models.task import Task
from app.domain.models.task_dependency import TaskDependency
from app.domain.models.note import Note
from app.domain.models.enums import DependencyType, TaskStatus
from app.application.ports.task_repository import TaskRepository
from app.application.ports.task_dependency_repository import TaskDependencyRepository
from app.application.ports.note_repository import NoteRepository
from app.application.ports.event_bus import EventBus
from app.application.events.domain_events import TaskBlocked
from app.domain.exceptions import BusinessRuleViolation


class AddTaskDependencyUseCase:
    """Use case for adding a task dependency (UC-010)."""
    
    def __init__(
        self,
        task_repository: TaskRepository,
        task_dependency_repository: TaskDependencyRepository,
        note_repository: NoteRepository,
        event_bus: EventBus,
    ):
        self.task_repository = task_repository
        self.task_dependency_repository = task_dependency_repository
        self.note_repository = note_repository
        self.event_bus = event_bus
    
    def _check_circular_dependency(
        self,
        task_id: UUID,
        depends_on_id: UUID,
    ) -> bool:
        """Check for circular dependencies (BR-008)."""
        # Simple check: if depends_on_id depends on task_id, it's circular
        deps = self.task_dependency_repository.find_by_task_id(depends_on_id)
        for dep in deps:
            if dep.depends_on_task_id == task_id:
                return True
            # Recursive check
            if self._check_circular_dependency(task_id, dep.depends_on_task_id):
                return True
        return False
    
    def execute(
        self,
        task_id: UUID,
        depends_on_task_id: UUID,
        dependency_type: DependencyType = DependencyType.BLOCKS,
    ) -> TaskDependency:
        """
        Add a task dependency.
        
        Flow:
        1. Validate both tasks exist
        2. Validate no circular dependency (BR-008)
        3. Create dependency
        4. If blocking and blocker not done, block task (BR-009)
        5. Emit TaskBlocked event if needed
        6. Create note
        7. Return dependency
        """
        # Validate tasks exist
        task = self.task_repository.find_by_id(task_id)
        if task is None:
            raise BusinessRuleViolation(
                f"Task with id {task_id} not found",
                code="task_not_found"
            )
        
        blocker_task = self.task_repository.find_by_id(depends_on_task_id)
        if blocker_task is None:
            raise BusinessRuleViolation(
                f"Task with id {depends_on_task_id} not found",
                code="blocker_task_not_found"
            )
        
        # BR-008: Check for circular dependency
        if self._check_circular_dependency(task_id, depends_on_task_id):
            raise BusinessRuleViolation(
                "Circular dependency detected",
                code="circular_dependency"
            )
        
        # Create dependency (domain validates self-dependency)
        dependency = TaskDependency.create(
            task_id=task_id,
            depends_on_task_id=depends_on_task_id,
            dependency_type=dependency_type,
        )
        
        # Save dependency
        self.task_dependency_repository.save(dependency)
        
        # BR-009: If blocking and blocker not done, block task
        if dependency_type == DependencyType.BLOCKS:
            if blocker_task.status != TaskStatus.DONE:
                task.block(f"Waiting on Task #{depends_on_task_id}")
                self.task_repository.save(task)

                # Emit event
                self.event_bus.emit(
                    TaskBlocked(
                        task_id=task_id,
                        reason=f"Waiting on Task #{depends_on_task_id}",
                        timestamp=datetime.now(UTC),
                    )
                )
        
        # Create note
        note = Note.create_system_note(
            task_id=task_id,
            content=f"Dependency added: Task #{depends_on_task_id}",
        )
        self.note_repository.save(note)
        
        return dependency
