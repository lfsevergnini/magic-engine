"""Base class for costs."""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..game import Game
    from ..player.player import Player
    from ..game_objects.base import GameObject

class Cost(ABC):
    """Interface for costs required to activate abilities or cast spells."""

    @abstractmethod
    def can_pay(self, player: 'Player', game: 'Game') -> bool:
        """Check if the player can currently pay this cost."""
        pass

    @abstractmethod
    def pay(self, player: 'Player', game: 'Game') -> None:
        """Deduct the cost from the player or modify game state accordingly."""
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass 