"""Interface for checking and performing state-based actions (SBAs)."""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..game import Game

class StateBasedActionChecker(ABC):
    """Handles the checking and execution of state-based actions."""
    @abstractmethod
    def check_and_perform(self, game: 'Game') -> bool:
        """Checks all game conditions requiring SBAs (e.g., lethal damage, 0 toughness, player loss)
           and performs them. Returns True if any actions were performed, False otherwise."""
        # This method will contain the logic for rule 704.5
        pass 