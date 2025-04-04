"""Interface for Spell objects on the stack."""
from abc import abstractmethod
from typing import List, TYPE_CHECKING

from .base import GameObject # Inherit from base GameObject

if TYPE_CHECKING:
    from ..game import Game
    # Define these properly later
    class TargetInfo:
        pass
    class Mode:
        pass
    class CastingCostInfo:
        pass

class Spell(GameObject):
    """Represents a spell (card being cast) currently on the stack."""
    targets: List['TargetInfo'] # Information about chosen targets
    chosen_modes: List['Mode'] # Information about chosen modes
    casting_cost_info: 'CastingCostInfo' # How the cost was paid (X value, alternative costs, additional costs)

    @abstractmethod
    def resolve(self, game: 'Game') -> None:
        """Executes the spell's effect(s) and moves it to the appropriate zone (usually graveyard)."""
        pass

    # May need methods for checking target legality on resolution (fizzle check) 