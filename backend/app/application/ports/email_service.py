"""Email service port."""
from typing import Protocol


class EmailService(Protocol):
    """Email service interface."""

    def send_magic_link(self, email: str, link: str) -> None:
        """Send a magic link email."""
        ...
