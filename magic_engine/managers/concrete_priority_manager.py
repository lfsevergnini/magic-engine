"""Concrete implementation of the PriorityManager for solitaire."""
from typing import Optional, TYPE_CHECKING

from .priority_manager import PriorityManager

if TYPE_CHECKING:
    from ..player.player import Player
    from ..game import Game

class SolitairePriorityManager(PriorityManager):
    """Manages priority for a single-player game. Always passes."""
    def __init__(self):
        self._player_with_priority: Optional['Player'] = None
        self._passed: bool = False

    def get_current_player(self) -> Optional['Player']:
        return self._player_with_priority

    def pass_priority(self, player: 'Player', game: 'Game') -> None:
        if player == self._player_with_priority:
            print(f"Player {player.id} passed priority.")
            self._player_with_priority = None # Priority is yielded
            self._passed = True
            # In solitaire, passing immediately leads to resolution/advancement
        else:
            print(f"Warning: Non-priority player {player.id} tried to pass priority.")

    def set_priority(self, player: Optional['Player']) -> None:
        """Gives priority to the specified player."""
        self._player_with_priority = player
        self._passed = False # Reset pass status when priority is gained
        if player:
            print(f"Priority set to Player {player.id}")
        else:
            print("Priority cleared.")

    def check_stack_resolve(self, game: 'Game') -> bool:
        """Checks if the single player has passed priority."""
        # In solitaire, if the player had priority and passed, resolve/advance.
        resolve = self._passed
        if resolve:
            self._passed = False # Reset for next priority cycle
        return resolve 