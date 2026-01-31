"""Mock email service implementation."""
from __future__ import annotations

from app.application.ports.email_service import EmailService


class MockEmailService(EmailService):
    """Mock email sender for MVP."""

    def __init__(self):
        self.sent = []

    def send_magic_link(self, email: str, link: str) -> None:
        """Record email send for testing."""
        self.sent.append({"email": email, "link": link})
