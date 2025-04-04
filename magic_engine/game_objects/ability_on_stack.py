"""Interface for Activated or Triggered Ability objects on the stack."""
from abc import abstractmethod
from typing import List, TYPE_CHECKING

from .base import GameObject # Inherit from base GameObject

if TYPE_CHECKING:
    from ..types import ObjectId
    from ..cards.ability_definition import AbilityDefinition
    from ..game import Game
    # Define these properly later
    class TargetInfo:
        pass
    class Mode:
        pass

class AbilityOnStack(GameObject):
    """Represents an activated or triggered ability currently on the stack."""
    source_id: 'ObjectId' # The ID of the GameObject that is the source of the ability
    ability_definition: 'AbilityDefinition' # The definition of the ability being resolved
    targets: List['TargetInfo'] # Information about chosen targets
    chosen_modes: List['Mode'] # Information about chosen modes
    # Note: Unlike Spells, these usually don't have card_data directly.
    # They might need owner/controller set based on the source object at creation.
    card_data = None # Abilities on stack don't have associated card data in the same way

    @abstractmethod
    def resolve(self, game: 'Game') -> None:
        """Executes the ability's effect(s). Abilities cease to exist after resolution."""
        pass

    # May need methods for checking target legality on resolution 