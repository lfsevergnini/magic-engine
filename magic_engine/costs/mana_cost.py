"""Interface for representing mana costs."""
from abc import abstractmethod
from typing import List, TYPE_CHECKING

from .base import Cost # Import base class

if TYPE_CHECKING:
    from ..enums import ManaSymbol
    from ..player.player import Player
    from ..game_objects.base import GameObject

class ManaCost(Cost):
    """Represents a specific mana cost component of a larger Cost."""
    symbols: List['ManaSymbol'] # Define ManaSymbol enum/class properly

    # ManaCost might need methods for calculating mana value, handling X, etc.

    @abstractmethod
    def get_mana_value(self) -> int:
        """Calculates the mana value (converted mana cost) of this cost."""
        pass

    # Override base methods if specific mana logic is needed
    @abstractmethod
    def is_payable(self, player: 'Player', source: 'GameObject') -> bool:
        # Implementation likely involves checking player.mana_pool
        pass

    @abstractmethod
    def pay(self, player: 'Player', source: 'GameObject') -> None:
        # Implementation likely involves calling player.mana_pool.spend
        pass 