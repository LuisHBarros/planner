"""UC-009: Rank Tasks use case."""
from datetime import datetime, UTC
from uuid import UUID
from typing import List

from app.domain.models.task import Task
from app.domain.services.ranking import calculate_rank_index, should_rebalance, rebalance_ranks
from app.application.ports.task_repository import TaskRepository
from app.application.ports.event_bus import EventBus
from app.application.events.domain_events import TasksReranked
from app.domain.exceptions import BusinessRuleViolation


class RankTasksUseCase:
    """Use case for ranking tasks (UC-009)."""
    
    def __init__(
        self,
        task_repository: TaskRepository,
        event_bus: EventBus,
    ):
        self.task_repository = task_repository
        self.event_bus = event_bus
    
    def execute(
        self,
        project_id: UUID,
        task_ids: List[UUID],
    ) -> List[Task]:
        """
        Rank tasks in a project.
        
        Flow:
        1. Load all tasks for project
        2. Validate all task_ids belong to project
        3. Calculate new rank_index values
        4. Update tasks
        5. Check if rebalancing needed
        6. Emit TasksReranked event
        7. Return updated tasks
        """
        # Load all tasks for project
        all_tasks = self.task_repository.find_by_project_id(project_id)
        task_dict = {task.id: task for task in all_tasks}
        
        # Validate all task_ids belong to project
        for task_id in task_ids:
            if task_id not in task_dict:
                raise BusinessRuleViolation(
                    f"Task {task_id} not found in project",
                    code="task_not_in_project"
                )
        
        # Calculate new rank_index values (BR-011)
        updated_tasks = []
        for position, task_id in enumerate(task_ids):
            task = task_dict[task_id]
            # Get tasks that come before this position
            before_tasks = [task_dict[tid] for tid in task_ids[:position]]
            new_rank = calculate_rank_index(position, before_tasks)
            task.rank_index = new_rank
            updated_tasks.append(task)
        
        # Check if rebalancing needed
        sorted_tasks = sorted(all_tasks, key=lambda t: t.rank_index)
        if should_rebalance(sorted_tasks):
            rebalance_ranks(sorted_tasks)
            updated_tasks = sorted_tasks
        
        # Save all updated tasks
        for task in updated_tasks:
            self.task_repository.save(task)

        # Emit event
        self.event_bus.emit(
            TasksReranked(
                project_id=project_id,
                task_ids=task_ids,
                timestamp=datetime.now(UTC),
            )
        )
        
        return updated_tasks
