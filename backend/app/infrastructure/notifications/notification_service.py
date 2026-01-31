"""Notification service implementation (mock)."""
from __future__ import annotations

from typing import Any, Dict, List


class NotificationService:
    """Mock notification service for MVP."""

    def __init__(self) -> None:
        self.sent: List[Dict[str, Any]] = []

    def send_manager_daily_report(self, project_id=None, user_id=None) -> None:
        """Send daily report notification."""
        self.sent.append({
            "type": "manager_daily_report",
            "project_id": project_id,
            "user_id": user_id,
        })

    def send_workload_alert(self, project_id=None, user_id=None) -> None:
        """Send workload alert notification."""
        self.sent.append({
            "type": "workload_alert",
            "project_id": project_id,
            "user_id": user_id,
        })

    def send_new_task_toast(self, project_id=None, task_id=None, user_id=None) -> None:
        """Send new task toast notification."""
        self.sent.append({
            "type": "new_task_toast",
            "project_id": project_id,
            "task_id": task_id,
            "user_id": user_id,
        })

    def send_employee_daily_email(self, project_id=None, user_id=None) -> None:
        """Send employee daily email notification."""
        self.sent.append({
            "type": "employee_daily_email",
            "project_id": project_id,
            "user_id": user_id,
        })

    def send_project_deadline_warning(self, project_id=None) -> None:
        """Send project deadline warning notification."""
        self.sent.append({
            "type": "project_deadline_warning",
            "project_id": project_id,
        })
