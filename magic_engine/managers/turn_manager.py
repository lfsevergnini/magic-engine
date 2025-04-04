"""Interface for managing the phases and steps of a turn."""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..enums import PhaseType, StepType
    from ..player.player import Player
    from ..game import Game

class TurnManager(ABC):
    """Handles turn progression through phases and steps."""
    current_phase: 'PhaseType'
    current_step: 'StepType'
    active_player: 'Player'
    turn_number: int = 0

    @abstractmethod
    def advance(self, game: 'Game') -> None:
        """Moves the game to the next step or phase, handling turn-based actions (untap, draw, cleanup)."""
        pass

    @abstractmethod
    def current_turn_player(self) -> 'Player':
        """Returns the player whose turn it currently is."""
        pass

    @abstractmethod
    def set_active_player(self, player: 'Player') -> None:
        """Sets the active player (e.g., at the start of a turn)."""
        pass

    @abstractmethod
    def start_turn(self, game: 'Game') -> None:
        """Performs actions needed at the very beginning of a turn."""
        pass 