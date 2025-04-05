from typing import TYPE_CHECKING
from .base import ActionCommand

if TYPE_CHECKING:
    from ..game import Game
    from ..player.player import Player


class PassPriorityCommand(ActionCommand):
    """Command to pass priority."""

    def execute(self, game: 'Game', player: 'Player') -> None:
        game.priority_manager.pass_priority(player, game)

    def get_display_name(self) -> str:
        return "Pass Priority"

    @staticmethod
    def is_legal(game: 'Game', player: 'Player') -> bool:
        # Passing priority is always legal when a player has priority.
        # The game loop ensures this is only offered when the player *has* priority.
        return True 