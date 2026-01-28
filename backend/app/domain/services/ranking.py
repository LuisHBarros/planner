"""Ranking service for task ordering (BR-011)."""
from typing import List
from app.domain.models.task import Task


def calculate_rank_index(position: int, existing_tasks: List[Task]) -> float:
    """
    Calculate rank_index for inserting a task at a specific position (BR-011).
    
    Float-based ranking allows insertion without renumbering.
    """
    if not existing_tasks:
        return 1.0
    
    if position == 0:
        # Insert at beginning
        return existing_tasks[0].rank_index - 1.0
    
    if position >= len(existing_tasks):
        # Insert at end
        return existing_tasks[-1].rank_index + 1.0
    
    # Insert between two tasks
    prev_rank = existing_tasks[position - 1].rank_index
    next_rank = existing_tasks[position].rank_index
    return (prev_rank + next_rank) / 2.0


def rebalance_ranks(tasks: List[Task]) -> None:
    """
    Rebalance rank_index values when they get too close (<0.001).
    
    Resets all ranks to evenly spaced values: 10, 20, 30, ...
    """
    for idx, task in enumerate(tasks):
        task.rank_index = (idx + 1) * 10.0


def should_rebalance(tasks: List[Task]) -> bool:
    """Check if ranks need rebalancing (adjacent ranks differ by <0.001)."""
    if len(tasks) < 2:
        return False
    
    sorted_tasks = sorted(tasks, key=lambda t: t.rank_index)
    for i in range(len(sorted_tasks) - 1):
        diff = abs(sorted_tasks[i + 1].rank_index - sorted_tasks[i].rank_index)
        if diff < 0.001:
            return True
    return False
