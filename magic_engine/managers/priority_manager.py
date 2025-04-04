"""Interface for managing player priority."""
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..player.player import Player
    from ..game import Game

class PriorityManager(ABC):
    """Manages which player has priority to take actions."""
    @abstractmethod
    def get_current_player(self) -> Optional['Player']:
        """Returns the player who currently holds priority, or None if none."""
        pass

    @abstractmethod
    def pass_priority(self, player: 'Player', game: 'Game') -> None:
        """Handles a player passing priority. If all players pass in succession, the top stack object resolves or the current step/phase ends."""
        pass

    @abstractmethod
    def set_priority(self, player: 'Player') -> None:
        """Gives priority to the specified player."""
        pass

    @abstractmethod
    def check_stack_resolve(self, game: 'Game') -> bool:
        """Checks if the stack should resolve (i.e., all players passed priority). Returns True if resolution should happen."""
        pass 