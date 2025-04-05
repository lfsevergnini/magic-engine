"""Concrete implementation of the PriorityManager for solitaire."""
from typing import Optional, TYPE_CHECKING, List

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

class TwoPlayerPriorityManager(PriorityManager):
    """Manages priority for a two-player game using APNAP order."""
    def __init__(self, players: List['Player']):
        if len(players) != 2:
            raise ValueError("TwoPlayerPriorityManager requires exactly two players.")
        # Assuming the first player in the list is the starting player initially
        self._players = players
        self._player_with_priority: Optional['Player'] = None
        # Track who passed *since the stack became empty OR an object was added/resolved*
        # For simplicity now, just track who passed since priority was last *set* to the AP.
        self._passed_priority_in_succession: List['Player'] = []

    def get_current_player(self) -> Optional['Player']:
        """Returns the player who currently holds priority."""
        return self._player_with_priority

    def pass_priority(self, player: 'Player', game: 'Game') -> None:
        """Handles a player passing priority. Switches priority to the other player.
        Keeps track of consecutive passes to determine stack resolution."""
        if player != self._player_with_priority:
            print(f"[Priority] Warning: Non-priority player {player.id} tried to pass.")
            return

        print(f"[Priority] Player {player.id} passed priority.")
        if player not in self._passed_priority_in_succession:
             self._passed_priority_in_succession.append(player)
        else:
             # This shouldn't happen if set_priority clears the list correctly, but good for safety
             print(f"[Priority] Warning: Player {player.id} already in passed list.")

        # Determine the other player
        other_player = self._players[0] if player == self._players[1] else self._players[1]

        # If the other player *also* just passed (meaning the list now has both),
        # priority is yielded completely until the next time it's set (e.g., after resolution/step change).
        # The check_stack_resolve method will handle this state.
        if other_player in self._passed_priority_in_succession:
             print(f"[Priority] Both players passed in succession.")
             self._player_with_priority = None
        else:
             # Otherwise, pass priority to the other player
             # Directly set the next player with priority *without* clearing the pass list.
             # set_priority (which clears the list) is only called after actions or turn progression.
             self._player_with_priority = other_player
             print(f"[Priority] Priority passed to Player {other_player.id}")

    def set_priority(self, player: Optional['Player']) -> None:
        """Gives priority to the specified player and resets pass tracking."""
        self._player_with_priority = player
        # Crucially, reset the list whenever priority is *actively set* to a player.
        # This means passing only counts *within* a single priority cycle.
        self._passed_priority_in_succession = []
        if player:
            print(f"[Priority] Priority set to Player {player.id}")
        # else:
            # print("[Priority] Priority cleared (e.g., during resolution).") # Covered by pass_priority print

    def check_stack_resolve(self, game: 'Game') -> bool:
        """Checks if both players have passed priority in succession."""
        # Stack resolves if there's no player currently holding priority,
        # which happens *after* the second player passes in pass_priority.
        resolve = self._player_with_priority is None and len(self._passed_priority_in_succession) == 2

        if resolve:
            print("[Priority] Stack resolution condition met.")
            # Reset pass list after resolution check confirms it.
            self._passed_priority_in_succession = []
        return resolve 