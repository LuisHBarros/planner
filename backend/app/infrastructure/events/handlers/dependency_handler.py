"""Event handler for task dependency events (auto-unblock)."""
from datetime import datetime, UTC
from typing import List

from app.infrastructure.events.in_memory_event_bus import InMemoryEventBus
from app.application.events.domain_events import TaskCompleted, TaskUnblocked
from app.application.ports.task_repository import TaskRepository
from app.application.ports.task_dependency_repository import TaskDependencyRepository
from app.domain.models.enums import TaskStatus


class DependencyHandler:
    """Handles dependency-related events (BR-009/UC-015)."""

    def __init__(
        self,
        event_bus: InMemoryEventBus,
        task_repository: TaskRepository,
        task_dependency_repository: TaskDependencyRepository,
    ) -> None:
        self.event_bus = event_bus
        self.task_repository = task_repository
        self.task_dependency_repository = task_dependency_repository

    def register(self) -> None:
        """Register event handlers."""

        def on_task_completed(event: TaskCompleted) -> None:
            """Unblock dependent tasks when a task is completed."""
            # Find all dependencies where this task is the blocker
            deps = self.task_dependency_repository.find_by_depends_on_task_id(
                event.task_id
            )
            for dep in deps:
                task = self.task_repository.find_by_id(dep.task_id)
                if not task or task.status != TaskStatus.BLOCKED:
                    continue
                # Check if all dependencies for this task are done
                all_deps = self.task_dependency_repository.find_by_task_id(task.id)
                all_done = True
                for d in all_deps:
                    blocker = self.task_repository.find_by_id(d.depends_on_task_id)
                    if blocker and blocker.status != TaskStatus.DONE:
                        all_done = False
                        break
                if all_done:
                    task.unblock()
                    self.task_repository.save(task)
                    self.event_bus.emit(
                        TaskUnblocked(
                            task_id=task.id,
                            timestamp=datetime.now(UTC),
                            user_id=event.user_id,
                        )
                    )

        self.event_bus.subscribe(TaskCompleted, on_task_completed)

