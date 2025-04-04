"""Base interface for game zones."""
from abc import ABC, abstractmethod
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import ZoneId, ObjectId
    from ..enums import ZoneType, VisibilityType
    from ..player.player import Player
    from ..game_objects.base import GameObject
    from ..game import Game # Needed for resolving IDs

class Zone(ABC):
    """Abstract base class for game zones (Library, Hand, Battlefield, etc.)."""
    id: 'ZoneId'
    zone_type: 'ZoneType'
    owner: Optional['Player'] # Some zones are player-specific
    visibility: 'VisibilityType'
    objects: List['ObjectId'] # Order matters for some zones (library, graveyard, stack)

    @abstractmethod
    def add(self, obj_id: 'ObjectId', position: Optional[int] = None) -> None:
        """Adds an object ID to the zone, optionally at a specific position."""
        pass

    @abstractmethod
    def remove(self, obj_id: 'ObjectId') -> None:
        """Removes an object ID from the zone."""
        pass

    @abstractmethod
    def contains(self, obj_id: 'ObjectId') -> bool:
        """Checks if an object ID is currently in the zone."""
        pass

    @abstractmethod
    def get_objects(self, game: 'Game') -> List['GameObject']:
        """Retrieves the actual GameObject instances corresponding to the IDs in the zone."""
        pass

    @abstractmethod
    def get_object_ids(self) -> List['ObjectId']:
        """Returns the list of object IDs currently in the zone."""
        pass

    # Helper methods might include get_count(), is_empty(), shuffle() (for library) 