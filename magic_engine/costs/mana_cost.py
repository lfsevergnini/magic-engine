"""Interface for representing mana costs."""
from abc import abstractmethod
from typing import List, TYPE_CHECKING, Dict

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

class SimpleManaCost(ManaCost):
    """A basic implementation of ManaCost for simple mana symbols."""

    def __init__(self, symbols: List['ManaSymbol']):
        # Basic validation/parsing could happen here
        self.symbols = symbols

    def get_mana_value(self) -> int:
        """Calculates the mana value. Handles generic and colored symbols.
           Does not handle X, phyrexian, hybrid yet.
        """
        value = 0
        generic_map: Dict[ManaSymbol, int] = {
            ManaSymbol.GENERIC_0: 0,
            ManaSymbol.GENERIC_1: 1,
            ManaSymbol.GENERIC_2: 2,
            # ... add more generic symbols as needed
        }
        for symbol in self.symbols:
            if symbol in generic_map:
                value += generic_map[symbol]
            elif symbol in [ManaSymbol.W, ManaSymbol.U, ManaSymbol.B, ManaSymbol.R, ManaSymbol.G, ManaSymbol.C, ManaSymbol.SNOW]:
                value += 1 # Colored, Colorless, Snow symbols count as 1 MV
            elif symbol == ManaSymbol.X:
                # Mana value of X is 0 in the cost itself
                pass
            # Add logic for hybrid, phyrexian etc. later
        return value

    def is_payable(self, player: 'Player', source: 'GameObject') -> bool:
        # TODO: Implement actual check against player.mana_pool
        # This is complex due to different mana types and restrictions.
        # For now, assume it's payable if the check reaches here.
        print(f"Warning: ManaCost.is_payable for {self.symbols} not fully implemented.")
        return True # Placeholder

    def pay(self, player: 'Player', source: 'GameObject') -> None:
        # TODO: Implement actual mana spending from player.mana_pool
        # This involves choosing which mana to spend if multiple options exist.
        print(f"Warning: ManaCost.pay for {self.symbols} not fully implemented.")
        pass # Placeholder

    def __repr__(self) -> str:
        return f"SimpleManaCost({[s.name for s in self.symbols]})" 