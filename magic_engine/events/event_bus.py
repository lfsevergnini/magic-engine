"""Interface for the event bus system."""
from abc import ABC, abstractmethod
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .base import Event

class EventBus(ABC):
    """Handles publishing and subscribing to game events."""
    @abstractmethod
    def subscribe(self, event_type: str, callback: Callable[['Event'], None]) -> None:
        """Registers a callback for a specific event type."""
        pass

    @abstractmethod
    def publish(self, event: 'Event') -> None:
        """Dispatches an event to all registered subscribers."""
        pass 