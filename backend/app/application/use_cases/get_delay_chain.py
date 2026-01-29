"""UC-030: Get Delay Chain Use Case.

Retrieves the complete causal chain of delays for a task,
enabling root cause analysis of why a task was delayed.
"""
from typing import Optional, Dict
from uuid import UUID

from app.application.ports.unit_of_work import UnitOfWork
from app.application.use_cases.dtos import DelayChainOutputDTO, DelayChainEntryDTO
from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.enums import ScheduleChangeReason


class GetDelayChainUseCase:
    """Use case for retrieving a task's delay chain (UC-030).

    This use case reconstructs the causal chain of schedule changes
    for a task, walking backwards through caused_by_task_id to find
    the root cause of delays.

    Example output:
        Task D is 4 days delayed
        ↳ 2026-12-20 12:00: Shifted by Task C (2 days)
           ↳ 2026-12-18 14:30: Shifted by Task B (2 days)
              ↳ 2026-12-18 09:15: Shifted by Task A (4 days)
                 ↳ Reason: Task A completed with actual_end > expected_end
    """

    def __init__(self, uow: UnitOfWork) -> None:
        """Initialize use case with unit of work.

        Args:
            uow: Unit of work for repository access
        """
        self.uow = uow

    def execute(self, task_id: UUID) -> DelayChainOutputDTO:
        """Execute the delay chain retrieval.

        Args:
            task_id: ID of the task to get delay chain for

        Returns:
            DelayChainOutputDTO with complete causal chain

        Raises:
            BusinessRuleViolation: If task not found
        """
        with self.uow:
            # Get the task
            task = self.uow.tasks.find_by_id(task_id)
            if task is None:
                raise BusinessRuleViolation(
                    f"Task with id {task_id} not found",
                    code="task_not_found"
                )

            # Get schedule history for this task
            history_entries = self.uow.schedule_history.find_by_task_id(task_id)

            # Build a cache of task titles for efficient lookup
            task_title_cache: Dict[UUID, str] = {task_id: task.title}

            # Build delay chain entries
            entries = []
            root_cause_task_id: Optional[UUID] = None
            root_cause_task_title: Optional[str] = None

            for history in history_entries:
                # Get caused_by task title if applicable
                caused_by_title: Optional[str] = None
                if history.caused_by_task_id:
                    if history.caused_by_task_id not in task_title_cache:
                        caused_by_task = self.uow.tasks.find_by_id(
                            history.caused_by_task_id
                        )
                        if caused_by_task:
                            task_title_cache[history.caused_by_task_id] = (
                                caused_by_task.title
                            )
                    caused_by_title = task_title_cache.get(history.caused_by_task_id)

                    # Track root cause (first entry in chain with caused_by)
                    if history.reason == ScheduleChangeReason.DEPENDENCY_DELAY:
                        # Walk to find root cause
                        current_cause_id = history.caused_by_task_id
                        visited = {task_id}
                        while current_cause_id and current_cause_id not in visited:
                            visited.add(current_cause_id)
                            # Check if this task has history entries
                            cause_history = self.uow.schedule_history.find_by_task_id(
                                current_cause_id
                            )
                            if not cause_history:
                                # This is the root cause (task that actually delayed)
                                root_cause_task_id = current_cause_id
                                if current_cause_id not in task_title_cache:
                                    root_task = self.uow.tasks.find_by_id(
                                        current_cause_id
                                    )
                                    if root_task:
                                        task_title_cache[current_cause_id] = (
                                            root_task.title
                                        )
                                root_cause_task_title = task_title_cache.get(
                                    current_cause_id
                                )
                                break
                            else:
                                # Continue walking the chain
                                last_entry = cause_history[-1]
                                if last_entry.caused_by_task_id:
                                    current_cause_id = last_entry.caused_by_task_id
                                else:
                                    # This task is the root
                                    root_cause_task_id = current_cause_id
                                    root_cause_task_title = task_title_cache.get(
                                        current_cause_id
                                    )
                                    break

                entry = DelayChainEntryDTO(
                    task_id=history.task_id,
                    task_title=task.title,
                    old_expected_start=history.old_expected_start,
                    old_expected_end=history.old_expected_end,
                    new_expected_start=history.new_expected_start,
                    new_expected_end=history.new_expected_end,
                    reason=history.reason,
                    caused_by_task_id=history.caused_by_task_id,
                    caused_by_task_title=caused_by_title,
                    changed_by_user_id=history.changed_by_user_id,
                    created_at=history.created_at,
                )
                entries.append(entry)

            # Calculate total delay
            total_delay_days: Optional[float] = None
            if task.is_delayed and task.actual_end_date and task.expected_end_date:
                delay_delta = task.actual_end_date - task.expected_end_date
                total_delay_days = delay_delta.total_seconds() / 86400  # seconds in a day

            return DelayChainOutputDTO(
                task_id=task_id,
                task_title=task.title,
                is_delayed=task.is_delayed,
                total_delay_days=total_delay_days,
                entries=entries,
                root_cause_task_id=root_cause_task_id,
                root_cause_task_title=root_cause_task_title,
            )
