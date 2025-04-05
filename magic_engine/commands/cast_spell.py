from typing import TYPE_CHECKING, Optional, List
from .base import ActionCommand
from ..enums import CardType, ZoneType, PhaseType

if TYPE_CHECKING:
    from ..game import Game
    from ..player.player import Player
    from ..game_objects.base import GameObject
    from ..constants import ZoneId


class CastSpellCommand(ActionCommand):
    """Command to cast a spell (from hand, initially)."""

    def __init__(self, spell_to_cast: 'GameObject'):
        # Requires the specific spell object to cast
        self.spell_to_cast = spell_to_cast

    def execute(self, game: 'Game', player: 'Player') -> None:
        """Handles moving the spell to the stack."""
        # --- TODO: Cost Payment --- 
        # 1. Announce spell: Move from hand to stack
        # 2. Check legality (can pay costs, valid targets if any)
        # 3. Pay costs (mana, additional costs)
        # 4. Put on stack (already done?)
        # For now, just move to stack without cost check.

        if not self.spell_to_cast:
            print("[Action] Error: CastSpellCommand executed without a spell.")
            return

        if not self.is_legal(game, player):
            print(f"[Action] Cannot cast {self.spell_to_cast.card_data.name}: not legal currently.")
            # Don't pass priority, let player choose something else
            return

        hand = player.get_hand()
        stack = game.get_stack()

        # Ensure the spell is actually in hand (basic check)
        if self.spell_to_cast.id not in hand.get_object_ids():
            print(f"[Action] Error: Spell {self.spell_to_cast.card_data.name} (ID: {self.spell_to_cast.id}) not found in hand.")
            return

        print(f"[Action] Player {player.id} casting {self.spell_to_cast.card_data.name}...")
        hand.remove(self.spell_to_cast.id)
        stack.add(self.spell_to_cast.id) # Add to top of stack
        self.spell_to_cast.zone = stack # Update the object's zone

        print(f"[Action] {self.spell_to_cast.card_data.name} moved to the stack.")

        # --- TODO: Target Selection (if required by the spell) --- 

        # Player retains priority after casting a spell to allow responses
        game.priority_manager.set_priority(player)
        # SBAs are checked after a spell is cast? (Rule 117.5 - yes, before priority)
        game.check_state_based_actions()

    def get_display_name(self) -> str:
        return f"Cast Spell: {self.spell_to_cast.card_data.name}" if self.spell_to_cast and self.spell_to_cast.card_data else "Cast Spell"

    @staticmethod
    def is_legal(game: 'Game', player: 'Player') -> bool:
        """Checks if the general action of casting *some* spell is legal."""
        # Basic legality: Can only cast sorcery-speed spells (like creatures)
        # during your main phase when the stack is empty and you have priority.
        # Instants have different timing.

        # TODO: Differentiate timing (sorcery vs instant speed)
        # For now, assume sorcery speed for simplicity

        is_main_phase = game.turn_manager.current_phase in [PhaseType.PRECOMBAT_MAIN, PhaseType.POSTCOMBAT_MAIN]
        is_turn_player = player == game.turn_manager.current_turn_player()
        stack_is_empty = game.get_stack().is_empty()

        # Check basic timing rules (Sorcery speed)
        if not (is_turn_player and is_main_phase and stack_is_empty):
            return False

        # Check if there is *any* castable spell in hand
        # TODO: Add cost check here eventually
        hand = player.get_hand()
        hand_objects = [game.get_object(oid) for oid in hand.get_object_ids()]

        has_castable_spell = any(
            obj and obj.card_data and 
            # Check if it's a type that can be cast (not land)
            not any(ct == CardType.LAND for ct in obj.card_data.card_types) and
            # TODO: Check if player can pay the mana cost
            True # Placeholder for cost check
            for obj in hand_objects
        )
        return has_castable_spell

    # Helper to check if a SPECIFIC spell can be cast (useful for generating commands)
    @staticmethod
    def can_cast_specific_spell(game: 'Game', player: 'Player', spell: 'GameObject') -> bool:
        """Checks if a specific spell object can be legally cast by the player right now."""
        if not spell or not spell.card_data:
            return False
        
        # Basic legality: Can only cast sorcery-speed spells (like creatures)
        # during your main phase when the stack is empty and you have priority.
        # TODO: Handle instant speed later.
        is_main_phase = game.turn_manager.current_phase in [PhaseType.PRECOMBAT_MAIN, PhaseType.POSTCOMBAT_MAIN]
        is_turn_player = player == game.turn_manager.current_turn_player()
        stack_is_empty = game.get_stack().is_empty()

        # Check timing (assume sorcery speed for now)
        is_sorcery_speed = not any(ct == CardType.INSTANT for ct in spell.card_data.card_types)
        if is_sorcery_speed and not (is_turn_player and is_main_phase and stack_is_empty):
            return False
        # TODO: Add instant speed timing check (any time player has priority)

        # Check if it's in hand
        if spell.id not in player.get_hand().get_object_ids():
             return False # Cannot cast from other zones yet
        
        # --- TODO: Check Mana Cost Payment --- 
        # Placeholder: Assume costs can always be paid for now
        can_pay_cost = True
        if not can_pay_cost:
             return False
        
        # --- TODO: Check Target Legality (if spell has targets) --- 
        # Placeholder: Assume no targets or targets are valid
        targets_ok = True
        if not targets_ok:
             return False

        return True 