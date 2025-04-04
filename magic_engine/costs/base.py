"""Base interface for game costs."""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..player.player import Player
    from ..game_objects.base import GameObject

class Cost(ABC):
    """Represents payment requirements for actions (spells, abilities)."""

    # Subclasses will define specific costs (ManaCost, TapCost, SacrificeCost, etc.)
    # Potentially properties for mana, life, tapping, sacrificing, discarding etc.

    @abstractmethod
    def is_payable(self, player: 'Player', source: 'GameObject') -> bool:
        """Checks if the player can currently pay this cost for the given source."""
        pass

    @abstractmethod
    def pay(self, player: 'Player', source: 'GameObject') -> None:
        """Executes the payment of the cost by the player."""
        pass 