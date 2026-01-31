"""LLM service implementation with optional HTTP call."""
from __future__ import annotations

import json
import os
from urllib import request

from app.application.ports.llm_service import LlmService
from app.domain.models.task import Task


class SimpleLlmService(LlmService):
    """LLM service with optional HTTP API and fallback."""

    def __init__(self, api_url: str | None = None, api_key: str | None = None):
        self.api_url = api_url or os.getenv("LLM_API_URL")
        self.api_key = api_key or os.getenv("LLM_API_KEY")

    def calculate_task_difficulty(self, task: Task) -> int:
        """Calculate task difficulty using LLM or fallback heuristic."""
        payload = {"title": task.title, "description": task.description}
        response = self._call_llm(payload)
        if isinstance(response, dict) and "difficulty" in response:
            return int(response["difficulty"])
        return self._fallback_difficulty(task)

    def calculate_task_progress(self, task: Task) -> int:
        """Calculate task progress using LLM or fallback heuristic."""
        payload = {"title": task.title, "description": task.description}
        response = self._call_llm(payload)
        if isinstance(response, dict) and "progress" in response:
            return int(response["progress"])
        return 0

    def _call_llm(self, payload: dict) -> dict | None:
        if not self.api_url or not self.api_key:
            return None
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.api_url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=10) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)
        except Exception:
            return None

    @staticmethod
    def _fallback_difficulty(task: Task) -> int:
        size = len(task.title) + (len(task.description) if task.description else 0)
        return max(1, min(10, size // 20 + 1))
