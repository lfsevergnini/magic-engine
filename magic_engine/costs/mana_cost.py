"""Interface for representing mana costs."""
from abc import abstractmethod
from typing import List, TYPE_CHECKING, Dict

from .base import Cost # Import base class
from ..enums import ManaType # Import ManaType

if TYPE_CHECKING:
    # Remove ManaSymbol import if no longer used directly
    # from ..enums import ManaSymbol 
    from ..player.player import Player
    from ..game_objects.base import GameObject

class ManaCost(Cost):
    """Represents a specific mana cost component of a larger Cost."""
    # Changed symbols to a dict storing counts of each mana type
    # symbols: List['ManaSymbol'] 
    cost_dict: Dict[ManaType | str, int] # e.g., {ManaType.WHITE: 1, ManaType.GENERIC: 1}

    # ManaCost might need methods for calculating mana value, handling X, etc.

    @abstractmethod
    def get_mana_value(self) -> int:
        """Calculates the mana value (converted mana cost) of this cost."""
        pass

    # Use the signature from the base Cost class
    @abstractmethod
    def can_pay(self, player: 'Player', game: 'Game') -> bool:
        pass

    @abstractmethod
    def pay(self, player: 'Player', game: 'Game') -> None:
        pass

class SimpleManaCost(ManaCost):
    """A basic implementation of ManaCost using a dictionary."""

    def __init__(self, generic: int = 0, white: int = 0, blue: int = 0, black: int = 0, red: int = 0, green: int = 0, colorless: int = 0):
        self.cost_dict = {}
        if generic > 0: self.cost_dict[ManaType.GENERIC] = generic
        if white > 0: self.cost_dict[ManaType.WHITE] = white
        if blue > 0: self.cost_dict[ManaType.BLUE] = blue
        if black > 0: self.cost_dict[ManaType.BLACK] = black
        if red > 0: self.cost_dict[ManaType.RED] = red
        if green > 0: self.cost_dict[ManaType.GREEN] = green
        if colorless > 0: self.cost_dict[ManaType.COLORLESS] = colorless
        # TODO: Add X, Phyrexian, Hybrid, Snow etc.

        # Pre-calculate mana value
        self._mana_value = sum(v for k, v in self.cost_dict.items())

    def get_mana_value(self) -> int:
        """Returns the pre-calculated mana value."""
        return self._mana_value

    # Match the base Cost signature
    def can_pay(self, player: 'Player', game: 'Game') -> bool:
        """Checks if the player's mana pool can pay this cost."""
        # Game parameter is not strictly needed here, but matches base class
        return player.mana_pool.can_spend(self)

    # Match the base Cost signature
    def pay(self, player: 'Player', game: 'Game') -> None:
        """Instructs the player's mana pool to spend mana for this cost."""
        # Game parameter is not strictly needed here
        success = player.mana_pool.spend(self)
        if not success:
            raise RuntimeError(f"Failed to pay mana cost {self} for {player.id} - pool state might be inconsistent.")

    def __repr__(self) -> str:
        cost_parts = []
        if ManaType.GENERIC in self.cost_dict:
            cost_parts.append(f"{{{self.cost_dict[ManaType.GENERIC]}}}")
        # Define a consistent order for colored mana
        color_order = [ManaType.WHITE, ManaType.BLUE, ManaType.BLACK, ManaType.RED, ManaType.GREEN, ManaType.COLORLESS]
        for color in color_order:
            if color in self.cost_dict:
                cost_parts.extend([f"{{{color.name[0]}}}"] * self.cost_dict[color]) # e.g., {W}{W}
        return f"SimpleManaCost({''.join(cost_parts)})"
