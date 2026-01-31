"""LLM service port."""
from typing import Protocol

from app.domain.models.task import Task


class LlmService(Protocol):
    """LLM service interface."""

    def calculate_task_difficulty(self, task: Task) -> int:
        """Calculate task difficulty using an LLM."""
        ...

    def calculate_task_progress(self, task: Task) -> int:
        """Calculate task progress using an LLM."""
        ...
