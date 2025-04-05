from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..game import Game
    from ..player.player import Player


class ActionCommand(ABC):
    """Abstract base class for all player actions."""

    @abstractmethod
    def execute(self, game: 'Game', player: 'Player') -> None:
        """Executes the action."""
        pass

    @abstractmethod
    def get_display_name(self) -> str:
        """Returns a user-friendly name for the action (for menus)."""
        pass

    @staticmethod
    @abstractmethod
    def is_legal(game: 'Game', player: 'Player') -> bool:
        """
        Checks if the action is currently legal for the player.
        This is a static method because the legality check often doesn't
        require an instance of the command itself, just the game state.
        """
        pass

    def __str__(self) -> str:
        """Provides a default string representation, often the display name."""
        return self.get_display_name()
