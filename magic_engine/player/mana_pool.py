"""Interface for a player's mana pool."""
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..enums import ManaType
    from ..costs.mana_cost import ManaCost
    from ..types import ObjectId
    # Define placeholder or import ManaRestriction properly
    class ManaRestriction:
        pass

class ManaPool(ABC):
    """Stores mana available to a player."""
    @abstractmethod
    def add(self, mana_type: 'ManaType', amount: int, source_id: Optional['ObjectId'] = None, restriction: Optional['ManaRestriction'] = None) -> None:
        """Adds mana of a specific type to the pool."""
        pass

    @abstractmethod
    def can_spend(self, cost: 'ManaCost') -> bool:
        """Checks if the mana in the pool is sufficient to pay a given mana cost."""
        pass

    @abstractmethod
    def spend(self, cost: 'ManaCost') -> bool:
        """Attempts to spend mana from the pool to pay a cost. Returns success/failure."""
        pass

    @abstractmethod
    def get_amount(self, mana_type: 'ManaType') -> int:
        """Returns the amount of a specific type of mana currently in the pool."""
        pass

    @abstractmethod
    def empty(self) -> None:
        """Removes all mana from the pool."""
        pass

    # Add methods for querying restricted mana, total mana, etc. if needed 