"""Concrete cost implementations."""
from typing import TYPE_CHECKING
from .base import Cost

if TYPE_CHECKING:
    from ..game import Game
    from ..player.player import Player
    from ..game_objects.permanent import Permanent

class TapCost(Cost):
    """Represents the cost of tapping a specific permanent."""
    def __init__(self, source: 'Permanent'):
        self.source_permanent = source

    def can_pay(self, player: 'Player', game: 'Game') -> bool:
        """Can pay if the permanent is controlled by the player and is untapped."""
        return self.source_permanent.controller == player and \
               not self.source_permanent.is_tapped()

    def pay(self, player: 'Player', game: 'Game') -> None:
        """Taps the permanent."""
        # Note: Mana abilities often handle tapping separately as a game action,
        # but having the pay logic here is correct for other activated abilities.
        if self.can_pay(player, game):
            self.source_permanent.tap() # tap() handles the status change
        else:
            # This should ideally not happen if can_pay was checked first
            print(f"Warning: Cannot pay TapCost for {self.source_permanent}") 

    def __repr__(self) -> str:
        return f"TapCost<{self.source_permanent.card_data.name}>" 