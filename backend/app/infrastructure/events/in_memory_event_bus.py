"""In-memory event bus implementation."""
from typing import Any, Callable, Dict, List

from app.application.ports.event_bus import EventBus


class InMemoryEventBus(EventBus):
    """Simple in-memory event bus."""

    def __init__(self):
        self._handlers: Dict[type, List[Callable[[Any], None]]] = {}

    def register(self, event_type: type, handler: Callable[[Any], None]) -> None:
        """Register an event handler."""
        self._handlers.setdefault(event_type, []).append(handler)

    def emit(self, event: Any) -> None:
        """Emit event to registered handlers."""
        for handler in self._handlers.get(type(event), []):
            handler(event)
