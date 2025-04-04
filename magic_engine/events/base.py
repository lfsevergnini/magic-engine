"""Base interface for game events."""
from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Imports for type checking
    pass

class Event(ABC):
    """Base class for game events."""
    # Subclasses will define specific event types and data
    event_type: str # e.g., "SpellCast", "CreatureDies", "DamageDealt"

    # Common potential attributes (add in subclasses as needed):
    # source_id: Optional[ObjectId] = None
    # target_id: Optional[Targetable] = None
    # player_id: Optional[PlayerId] = None
    # amount: Optional[int] = None
    # related_object_id: Optional[ObjectId] = None

    def __init__(self, event_type: str):
        self.event_type = event_type 