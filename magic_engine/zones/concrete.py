"""Concrete implementations of Zone interfaces."""
import random
from typing import List, Optional, TYPE_CHECKING

from .base import Zone
from ..enums import ZoneType, VisibilityType

if TYPE_CHECKING:
    from ..types import ZoneId, ObjectId
    from ..player.player import Player
    from ..game_objects.base import GameObject
    from ..game import Game

class ConcreteZone(Zone):
    """A basic concrete implementation of a Zone."""
    def __init__(self, zone_id: 'ZoneId', zone_type: 'ZoneType', owner: Optional['Player'], visibility: 'VisibilityType'):
        self.id: 'ZoneId' = zone_id
        self.zone_type: 'ZoneType' = zone_type
        self.owner: Optional['Player'] = owner
        self.visibility: 'VisibilityType' = visibility
        self.objects: List['ObjectId'] = [] # Order matters for some zones

    def add(self, obj_id: 'ObjectId', position: Optional[int] = None) -> None:
        if position is None:
            # Default add to top/end (relevant for graveyard/stack)
            self.objects.append(obj_id)
        else:
            # Ensure position is valid
            pos = max(0, min(position, len(self.objects)))
            self.objects.insert(pos, obj_id)

    def remove(self, obj_id: 'ObjectId') -> None:
        try:
            self.objects.remove(obj_id)
        except ValueError:
            print(f"Warning: Tried to remove non-existent object {obj_id} from zone {self.id}")

    def contains(self, obj_id: 'ObjectId') -> bool:
        return obj_id in self.objects

    def get_objects(self, game: 'Game') -> List['GameObject']:
        """Retrieves the actual GameObject instances."""
        # Need error handling if an ID isn't found in game.objects
        return [game.get_object(obj_id) for obj_id in self.objects if game.get_object(obj_id) is not None]

    def get_object_ids(self) -> List['ObjectId']:
        return list(self.objects) # Return a copy

    def get_count(self) -> int:
        return len(self.objects)

    def is_empty(self) -> bool:
        return not self.objects

    def __repr__(self) -> str:
        owner_str = f" (Owner: {self.owner.id})" if self.owner else ""
        return f"Zone<{self.id} ({self.zone_type.name}){owner_str} ({self.get_count()} objects)>"

# --- Specific Zone Implementations ---

class Library(ConcreteZone):
    def __init__(self, zone_id: 'ZoneId', owner: 'Player'):
        super().__init__(zone_id, ZoneType.LIBRARY, owner, VisibilityType.HIDDEN_TO_ALL)

    def shuffle(self) -> None:
        print(f"Shuffling {self.id}")
        random.shuffle(self.objects)

    def draw(self) -> Optional['ObjectId']:
        """Removes and returns the top card's ID, or None if empty."""
        if not self.is_empty():
            # Library top is considered index 0
            return self.objects.pop(0)
        return None

    def add(self, obj_id: 'ObjectId', position: Optional[int] = None, to_bottom: bool = False) -> None:
        """Adds to library, defaulting to top unless specified otherwise."""
        if to_bottom:
            super().add(obj_id, position=len(self.objects))
        elif position is None:
             super().add(obj_id, position=0) # Default add to top
        else:
            super().add(obj_id, position=position)


class Hand(ConcreteZone):
    def __init__(self, zone_id: 'ZoneId', owner: 'Player'):
        super().__init__(zone_id, ZoneType.HAND, owner, VisibilityType.OWNER_ONLY)
        # Order in hand doesn't technically matter by rules, but useful for UI

class Battlefield(ConcreteZone):
    def __init__(self, zone_id: 'ZoneId' = "battlefield"): # Shared zone ID
        super().__init__(zone_id, ZoneType.BATTLEFIELD, None, VisibilityType.PUBLIC)
        # Order technically doesn't matter by rules, but list is convenient

class Graveyard(ConcreteZone):
     def __init__(self, zone_id: 'ZoneId', owner: 'Player'):
        super().__init__(zone_id, ZoneType.GRAVEYARD, owner, VisibilityType.PUBLIC)
        # Order matters - cards enter on top (end of list)

# Add Stack, Exile, Command later if needed 