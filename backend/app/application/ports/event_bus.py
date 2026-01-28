"""Event bus port interface."""
from typing import Protocol, Type, Any, Callable


class EventBus(Protocol):
    """Event bus interface for domain events."""
    
    def subscribe(self, event_type: Type, handler: Callable) -> None:
        """Subscribe a handler to an event type."""
        ...
    
    def emit(self, event: Any) -> None:
        """Emit an event to all subscribed handlers."""
        ...
