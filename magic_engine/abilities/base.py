"""Base class for all abilities."""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..game import Game
    from ..player.player import Player
    from ..game_objects.base import GameObject
    from ..costs.base import Cost

class Ability(ABC):
    """Interface for abilities that game objects can have."""
    source: 'GameObject' # The game object this ability belongs to
    controller: 'Player' # The player who controls the ability (usually same as source controller)
    cost: list['Cost'] # The costs to activate the ability (e.g., tap, mana)

    def __init__(self, source: 'GameObject', controller: 'Player', cost: list['Cost'] | None = None):
        self.source = source
        self.controller = controller
        self.cost = cost if cost else []

    @abstractmethod
    def can_activate(self, game: 'Game') -> bool:
        """Check if the ability can currently be activated (e.g., costs can be paid, targets valid)."""
        pass

    @abstractmethod
    def activate(self, game: 'Game') -> None:
        """Perform the ability's effect."""
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass 