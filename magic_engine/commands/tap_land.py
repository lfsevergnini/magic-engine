from typing import TYPE_CHECKING, Optional
from .base import ActionCommand
from ..enums import CardType, ManaType
from ..game_objects.permanent import Permanent

if TYPE_CHECKING:
    from ..game import Game
    from ..player.player import Player


class TapLandCommand(ActionCommand):
    """Command to tap a land for mana."""

    def __init__(self, land_to_tap: Optional['Permanent'] = None):
        self.land_to_tap = land_to_tap # Store the chosen land if pre-selected

    def execute(self, game: 'Game', player: 'Player') -> None:
        """Handles the process of tapping a land for mana."""
        if not self.is_legal(game, player):
            print("[Action] Cannot tap land: not legal.")
            # Tapping for mana doesn't pass priority usually
            return

        battlefield = game.get_zone("battlefield") # Use constant ZoneId.BATTLEFIELD ideally

        if self.land_to_tap:
            chosen_land_perm = self.land_to_tap
        else:
            controlled_perms = [p for p in battlefield.get_objects(game) if isinstance(p, Permanent) and p.controller == player]
            untapped_lands = [p for p in controlled_perms if p.card_data and CardType.LAND in p.card_data.card_types and not p.is_tapped()]

            if not untapped_lands:
                print("[Action] Error: tap_land action chosen but no untapped lands found (unexpected)." )
                return # Should not happen if is_legal passed

            chosen_land_perm = player.input_handler.choose_permanent_from_list(
                untapped_lands, "Choose an untapped land to tap for mana:"
            )

        if not chosen_land_perm:
            print("[Action] No land chosen to tap.")
            # Tapping for mana doesn't pass priority
            return

        print(f"[Action] Tapping {chosen_land_perm.card_data.name} for mana.")
        if hasattr(chosen_land_perm, 'tap'):
            chosen_land_perm.tap()
        else:
            print(f"Warning: Cannot tap object {chosen_land_perm} as it lacks a 'tap' method.")
            return

        # TODO: Refactor mana production logic (should be tied to the card/permanent itself)
        mana_produced: Optional[ManaType] = None
        if chosen_land_perm.card_data.name == "Plains":
            mana_produced = ManaType.WHITE
        elif chosen_land_perm.card_data.name == "Forest":
            mana_produced = ManaType.GREEN

        if mana_produced:
            player.mana_pool.add(mana_produced, 1)
            print(f"[Action] Added {{ {mana_produced.name}: 1 }} to Player {player.id}'s mana pool. Current: {player.mana_pool}")
        else:
            print(f"[Action] Warning: Don't know what mana {chosen_land_perm.card_data.name} produces.")

        # Mana abilities don't use the stack and don't pass priority, player retains it.
        game.priority_manager.set_priority(player)
        # SBAs *are* checked after mana abilities resolve
        game.check_state_based_actions()

    def get_display_name(self) -> str:
        if self.land_to_tap and self.land_to_tap.card_data:
            return f"Tap Land: {self.land_to_tap.card_data.name}"
        return "Tap Land"

    @staticmethod
    def is_legal(game: 'Game', player: 'Player') -> bool:
        # Check if tapping a land for mana is possible (as a mana ability)
        # Mana abilities can usually be activated anytime the player has priority
        # For simplicity now, let's keep it wide open, but restrict later if needed.
        # The main check is whether there's an untapped land they control.
        battlefield = game.get_zone("battlefield") # Use constant ZoneId.BATTLEFIELD ideally
        my_perms = [p for p in battlefield.get_objects(game) if isinstance(p, Permanent) and p.controller == player]
        return any(p.card_data and CardType.LAND in p.card_data.card_types and not p.is_tapped() for p in my_perms)
