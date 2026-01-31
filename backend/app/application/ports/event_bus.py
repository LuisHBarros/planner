"""Event bus port."""
from typing import Protocol, Any


class EventBus(Protocol):
    """Event bus interface."""

    def emit(self, event: Any) -> None:
        """Emit a domain event."""
        ...
