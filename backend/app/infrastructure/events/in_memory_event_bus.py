"""In-memory event bus implementation."""
from typing import Dict, List, Callable, Type, Any
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class InMemoryEventBus:
    """Simple in-memory event bus for MVP."""
    
    def __init__(self):
        self._handlers: Dict[Type, List[Callable]] = defaultdict(list)
    
    def subscribe(self, event_type: Type, handler: Callable):
        """Subscribe a handler to an event type."""
        self._handlers[event_type].append(handler)
    
    def emit(self, event: Any):
        """Emit an event to all subscribed handlers."""
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])
        
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error handling {event_type.__name__}: {e}", exc_info=True)
