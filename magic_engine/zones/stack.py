"""Interface for the Stack zone."""
from abc import abstractmethod
from typing import Optional, TYPE_CHECKING

from .base import Zone # Inherit from base Zone
from ..enums import ZoneType, VisibilityType

if TYPE_CHECKING:
    from ..types import ObjectId

class Stack(Zone):
    """Interface for the Stack, a specialized Zone."""
    zone_type = ZoneType.STACK
    visibility = VisibilityType.PUBLIC
    owner = None # The stack is a shared zone

    @abstractmethod
    def push(self, obj_id: 'ObjectId') -> None:
        """Adds an object (spell or ability) to the top of the stack."""
        # Likely calls self.add(obj_id, position=0 or -1 depending on list convention)
        pass

    @abstractmethod
    def pop(self) -> Optional['ObjectId']:
        """Removes and returns the top object ID from the stack. Returns None if empty."""
        pass

    @abstractmethod
    def peek(self) -> Optional['ObjectId']:
        """Returns the top object ID from the stack without removing it. Returns None if empty."""
        pass

    # Other stack-specific methods might be relevant (e.g., getting all objects) 