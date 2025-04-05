from typing import TYPE_CHECKING, Optional
from .base import ActionCommand
from ..enums import CardType, ZoneType, PhaseType
from ..game_objects.concrete import ConcretePermanent

if TYPE_CHECKING:
    from ..game import Game
    from ..player.player import Player
    from ..game_objects.base import GameObject
    from ..constants import ZoneId


class PlayLandCommand(ActionCommand):
    """Command to play a land from hand."""

    def __init__(self, land_to_play: Optional['GameObject'] = None):
        self.land_to_play = land_to_play # Store the chosen land if pre-selected

    def execute(self, game: 'Game', player: 'Player') -> None:
        """Handles the process of playing a land."""
        if not self.is_legal(game, player):
            print("[Action] Cannot play land: not legal.")
            game.priority_manager.pass_priority(player, game) # Maybe just return?
            return

        hand = player.get_hand()

        if self.land_to_play:
            chosen_land_obj = self.land_to_play
        else:
            # If not pre-selected, ask the player
            hand_objs = [game.get_object(oid) for oid in hand.get_object_ids()]
            land_cards_in_hand = [obj for obj in hand_objs if obj and obj.card_data and CardType.LAND in obj.card_data.card_types]
            if not land_cards_in_hand:
                print("[Action] Error: play_land action chosen but no land cards found in hand (unexpected)." )
                return # Should not happen if is_legal passed

            chosen_land_obj = player.input_handler.choose_card_from_list(
                land_cards_in_hand, "Choose a land to play:"
            )

        if not chosen_land_obj:
            print("[Action] No land chosen to play.")
            # Don't pass priority here, let the player choose again or pass explicitly
            return # Or should we pass?

        print(f"[Action] Playing {chosen_land_obj.card_data.name} from hand.")
        hand.remove(chosen_land_obj.id)
        battlefield = game.get_zone("battlefield") # Use constant ZoneId.BATTLEFIELD ideally
        battlefield.add(chosen_land_obj.id)
        chosen_land_obj.zone = battlefield
        chosen_land_obj.controller = player
        if isinstance(chosen_land_obj, ConcretePermanent):
            chosen_land_obj.enters_battlefield(game)

        player.lands_played_this_turn += 1
        print(f"[Action] {chosen_land_obj.card_data.name} entered the battlefield.")
        game.priority_manager.set_priority(player) # Player retains priority after playing land
        game.check_state_based_actions()

    def get_display_name(self) -> str:
        if self.land_to_play and self.land_to_play.card_data:
            return f"Play Land: {self.land_to_play.card_data.name}"
        return "Play Land"

    @staticmethod
    def is_legal(game: 'Game', player: 'Player') -> bool:
        # Check if playing a land is possible
        is_main_phase = game.turn_manager.current_phase in [PhaseType.PRECOMBAT_MAIN, PhaseType.POSTCOMBAT_MAIN]
        is_turn_player = player == game.turn_manager.current_turn_player()
        stack_is_empty = game.get_stack().is_empty()
        can_play_land = (is_turn_player and
                         is_main_phase and
                         stack_is_empty and
                         player.lands_played_this_turn < 1)
        if not can_play_land:
            return False

        # Check if there *is* a land in hand to play
        hand = player.get_hand()
        hand_objects = [game.get_object(oid) for oid in hand.get_object_ids()]
        return any(obj and obj.card_data and CardType.LAND in obj.card_data.card_types for obj in hand_objects)
