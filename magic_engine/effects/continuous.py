"""Interface for continuous effects."""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from .base import Effect # Inherit from base Effect

if TYPE_CHECKING:
    from ..types import Timestamp, Targetable
    from ..enums import LayerType
    from ..game import Game
    # Define these properly later
    class DependencyInfo:
        pass
    class Duration:
        pass

class ContinuousEffect(Effect):
    """Represents effects that modify game state or objects over a duration."""
    layer: 'LayerType' # Which layer this effect applies in
    timestamp: 'Timestamp' # Determines application order within a layer
    dependency_info: 'DependencyInfo' # Information for dependency calculations
    duration: 'Duration' # How long the effect lasts (e.g., permanent, until end of turn)

    @abstractmethod
    def apply(self, target: 'Targetable', game: 'Game') -> None:
        """Applies the modification of this effect to the target object/player/game state."""
        pass

    @abstractmethod
    def is_expired(self, game: 'Game') -> bool:
        """Checks if the effect's duration has ended."""
        pass

    # Continuous effects can modify characteristics, grant/remove abilities,
    # change control, change types, etc.
    # They can also be replacement or prevention effects.

class ReplacementEffect(ContinuousEffect):
    """Interface for effects that replace game events."""
    # Layer doesn't strictly apply to replacement effects in the same way,
    # but they are continuous. Duration is important.

    @abstractmethod
    def modifies(self, event: 'Event', game: 'Game') -> bool:
        """Checks if this effect applies to the given event."""
        pass

    @abstractmethod
    def replace(self, event: 'Event', game: 'Game') -> Optional['Event']:
        """Performs the replacement. Returns the modified event(s) or None if the event is fully replaced."""
        pass

class PreventionEffect(ContinuousEffect):
    """Interface for effects that prevent damage."""
    # Similar to replacement effects regarding layer/duration.

    @abstractmethod
    def prevents(self, damage_event: 'Event', game: 'Game') -> int:
        """Checks if this effect applies to the damage event and returns the amount of damage to prevent."""
        pass

    @abstractmethod
    def apply_prevention(self, amount_prevented: int, game: 'Game') -> None:
        """Applies the consequence of prevention (e.g., removing a shield counter)."""
        pass 