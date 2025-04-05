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
        """Handles announcing the spell, paying costs, and moving it to the stack."""
        # Process according to rule 601.2

        if not self.spell_to_cast or not self.spell_to_cast.card_data:
            print("[Action] Error: CastSpellCommand executed without a valid spell object.")
            return

        spell_card_data = self.spell_to_cast.card_data
        mana_cost = spell_card_data.mana_cost

        # 601.2a Announce: Already implicitly done by choosing this command
        # 601.2b Choose modes/targets etc. - TODO
        # 601.2c Check legality (timing, etc.) - Partially done in can_cast_specific_spell
        # Re-check timing and basic legality here to be safe
        if not CastSpellCommand.can_cast_specific_spell(game, player, self.spell_to_cast, check_costs=False):
            print(f"[Action] Cannot cast {spell_card_data.name}: Timing or other restriction failed.")
            return

        # 601.2e Check if costs can be paid
        if mana_cost and not player.mana_pool.can_spend(mana_cost):
             print(f"[Action] Cannot cast {spell_card_data.name}: Cannot pay mana cost {mana_cost}. Available: {player.mana_pool}")
             return
        # TODO: Check other costs (life, sacrifice etc.)

        # --- If all checks pass, proceed --- 
        print(f"[Action] Player {player.id} casting {spell_card_data.name}...")

        # 601.2h Move card to stack
        hand = player.get_hand()
        stack = game.get_stack()
        if self.spell_to_cast.id not in hand.get_object_ids(): # Final check
            print(f"[Action] Error: Spell {spell_card_data.name} (ID: {self.spell_to_cast.id}) not found in hand before moving to stack.")
            return
        hand.remove(self.spell_to_cast.id)
        stack.add(self.spell_to_cast.id) # Add to top of stack
        self.spell_to_cast.zone = stack
        print(f"[Action] {spell_card_data.name} moved to the stack.")

        # 601.2g Pay costs
        print(f"[Action] Paying costs for {spell_card_data.name}...")
        if mana_cost:
            try:
                player.pay_cost(mana_cost, self.spell_to_cast)
                print(f"[Action] Mana cost paid. Pool: {player.mana_pool}")
            except Exception as e: # Catch potential errors during payment
                 print(f"[Action] Error paying mana cost for {spell_card_data.name}: {e}")
                 # TODO: How to handle payment failure? Revert state? (Complex)
                 # For now, assume payment failure means the cast fails somehow.
                 # We might need a transaction system or careful state management.
                 # Simplest: Treat as illegal cast attempt if payment fails.
                 # Need to move card back? Rules are complex here (601.2h happens before 601.2g!)
                 # Let's assume pay_cost raises if it fails critically for now.
                 # Revert move to stack? Or just let it fizzle? Leave on stack for now.
                 return
        # TODO: Pay other costs

        # --- Spell is now successfully cast and on the stack --- 

        # Player gets priority after successfully casting (Rule 117.3c)
        game.priority_manager.set_priority(player)
        # SBAs checked before priority (Rule 117.5)
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
    def can_cast_specific_spell(game: 'Game', player: 'Player', spell: 'GameObject', check_costs: bool = True) -> bool:
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
        
        # --- Check Mana Cost Payment --- 
        if check_costs:
            mana_cost = spell.card_data.mana_cost
            if mana_cost and not player.mana_pool.can_spend(mana_cost):
                 return False # Cannot afford mana cost
            # TODO: Check other costs

        # --- TODO: Check Target Legality (if spell has targets) --- 
        # Placeholder: Assume no targets or targets are valid
        targets_ok = True
        if not targets_ok:
             return False

        return True 