"""Concrete implementation of the Player interface."""
from typing import Dict, Optional, TYPE_CHECKING, List, Any

from .player import Player
from ..enums import ZoneType, CounterType, ManaType, CardType, PhaseType
from ..zones.concrete import Library, Hand, Graveyard # Import concrete zones
from ..player.concrete_mana_pool import ConcreteManaPool # Import concrete pool
from ..game_objects.concrete import ConcretePermanent # Import concrete permanent

if TYPE_CHECKING:
    from ..types import PlayerId, ObjectId, CountersDict, SpellCastingOptions, AbilityActivationOptions, SpecialActionOptions, ChoiceOptions, ChoiceResult
    from ..player.mana_pool import ManaPool
    from ..zones.base import Zone
    from ..player.input_handler import PlayerInputHandler
    from ..costs.base import Cost
    from ..game_objects.base import GameObject
    from ..game import Game
    from ..cards.card_data import CardData

class ConcretePlayer(Player):
    """Concrete implementation for a player."""
    def __init__(self, player_id: 'PlayerId', game: 'Game', input_handler: 'PlayerInputHandler', life: int = 20):
        self.id: 'PlayerId' = player_id
        self.game: 'Game' = game
        self.input_handler: 'PlayerInputHandler' = input_handler
        self.life: int = life
        self.mana_pool: 'ManaPool' = ConcreteManaPool()
        self.counters: 'CountersDict' = {}

        # Initialize player-specific zones
        self.zones: Dict['ZoneType', 'Zone'] = {
            ZoneType.LIBRARY: Library(zone_id=f"library_{player_id}", owner=self),
            ZoneType.HAND: Hand(zone_id=f"hand_{player_id}", owner=self),
            ZoneType.GRAVEYARD: Graveyard(zone_id=f"graveyard_{player_id}", owner=self),
            # Command zone might be needed later
        }

        # --- Player State Attributes ---
        self.has_priority: bool = False
        self.has_lost: bool = False
        self.has_won: bool = False
        self.lands_played_this_turn: int = 0
        # Add other states as needed

    def get_library(self) -> Library:
        return self.zones[ZoneType.LIBRARY]

    def get_hand(self) -> Hand:
        return self.zones[ZoneType.HAND]

    def get_graveyard(self) -> Graveyard:
        return self.zones[ZoneType.GRAVEYARD]

    def draw_cards(self, number: int) -> None:
        library = self.get_library()
        hand = self.get_hand()
        print(f"Player {self.id} drawing {number} card(s). Lib size: {library.get_count()}")
        for _ in range(number):
            if library.is_empty():
                # TODO: Implement player losing the game (Rule 104.3b)
                print(f"Player {self.id} tried to draw from empty library! Game loss pending.")
                self.game.check_win_loss_condition() # Signal game to check
                break
            card_id = library.draw()
            if card_id:
                card_obj = self.game.get_object(card_id)
                if card_obj:
                    card_obj.move_to_zone(hand, self.game)
                else:
                     print(f"Error: Drawn card ID {card_id} not found in game objects.")
        print(f"Player {self.id} hand size: {hand.get_count()}")

    def lose_life(self, amount: int, source_id: Optional['ObjectId'] = None) -> None:
        # TODO: Publish LifeLostEvent
        print(f"Player {self.id} losing {amount} life. Current: {self.life}")
        self.life -= amount
        print(f"Player {self.id} new life total: {self.life}")
        self.game.check_win_loss_condition() # Signal game to check

    def gain_life(self, amount: int, source_id: Optional['ObjectId'] = None) -> None:
        # TODO: Publish LifeGainedEvent
        print(f"Player {self.id} gaining {amount} life. Current: {self.life}")
        self.life += amount
        print(f"Player {self.id} new life total: {self.life}")

    def can_pay_cost(self, cost: 'Cost', source: 'GameObject') -> bool:
        # TODO: Implement actual cost check (mana, life, tapping, sacrifice etc.)
        # For now, relies on the ManaPool's placeholder check
        if isinstance(cost, ManaCost):
             return self.mana_pool.can_spend(cost)
        print(f"Warning: can_pay_cost not implemented for non-ManaCost: {cost}")
        return True # Placeholder

    def pay_cost(self, cost: 'Cost', source: 'GameObject') -> None:
        # TODO: Implement actual cost payment
        if isinstance(cost, ManaCost):
            success = self.mana_pool.spend(cost)
            if not success:
                 print(f"Error: Failed to pay mana cost {cost} for Player {self.id}")
                 # This should ideally be prevented by can_pay_cost check
        else:
            print(f"Warning: pay_cost not implemented for non-ManaCost: {cost}")
        # Placeholder

    # --- Action Legality ---
    def can_cast(self, card_obj: 'GameObject', from_zone: 'Zone') -> bool:
        # Simplified check for now:
        # 1. Is it your turn?
        # 2. Is it the main phase?
        # 3. Is the stack empty? (Sorcery speed)
        # 4. Do you have priority?
        # 5. Can you pay the mana cost?
        # Ignores timing restrictions (Instant vs Sorcery), permissions (effects allowing cast)
        if not card_obj or not card_obj.card_data or not card_obj.card_data.mana_cost:
            return False # Cannot cast without card data/mana cost

        tm = self.game.turn_manager
        pm = self.game.priority_manager
        is_main_phase = tm.current_phase == PhaseType.PRECOMBAT_MAIN or tm.current_phase == PhaseType.POSTCOMBAT_MAIN
        is_my_turn = tm.current_turn_player() == self
        has_priority = pm.get_current_player() == self
        stack_empty = self.game.get_stack().is_empty()

        # Basic sorcery speed check
        if not (is_my_turn and is_main_phase and has_priority and stack_empty):
            # TODO: Check for Instant speed later
            return False

        # Check cost
        can_pay = self.can_pay_cost(card_obj.card_data.mana_cost, card_obj)
        return can_pay

    def can_activate(self, ability_source: 'GameObject', ability_index: int) -> bool:
        # TODO: Implement ability activation checks
        print("Warning: can_activate not implemented.")
        return False

    def can_play_land(self, card_obj: 'GameObject', from_zone: 'Zone') -> bool:
        # Check: Is it a land? Is it in the correct zone (usually hand)?
        # Is it your turn? Main phase? Stack empty? Priority? Land drop available?
        if not card_obj or not card_obj.card_data or CardType.LAND not in card_obj.card_data.card_types:
             return False
        if from_zone.zone_type != ZoneType.HAND or not from_zone.contains(card_obj.id):
            return False

        tm = self.game.turn_manager
        pm = self.game.priority_manager
        is_main_phase = tm.current_phase == PhaseType.PRECOMBAT_MAIN or tm.current_phase == PhaseType.POSTCOMBAT_MAIN
        is_my_turn = tm.current_turn_player() == self
        has_priority = pm.get_current_player() == self
        stack_empty = self.game.get_stack().is_empty()
        land_drop_available = self.lands_played_this_turn < 1 # Basic check

        can_play = is_my_turn and is_main_phase and has_priority and stack_empty and land_drop_available
        # print(f"can_play_land check for {card_obj}: {can_play} (Turn:{is_my_turn}, Phase:{is_main_phase}, Prio:{has_priority}, Stack:{stack_empty}, Drop:{land_drop_available})")
        return can_play

    # --- Action Performance ---
    def cast_spell(self, card_obj: 'GameObject', from_zone: 'Zone', options: 'SpellCastingOptions') -> None:
        # TODO: Implement spell casting (move to stack, pay costs, handle targets/modes)
        print(f"Warning: cast_spell for {card_obj} not implemented.")
        pass

    def activate_ability(self, ability_source: 'GameObject', ability_index: int, options: 'AbilityActivationOptions') -> None:
        # TODO: Implement ability activation
        print(f"Warning: activate_ability for {ability_source} not implemented.")
        pass

    def play_land(self, card_obj: 'GameObject', from_zone: 'Zone') -> None:
        if not self.can_play_land(card_obj, from_zone):
            print(f"Error: Cannot legally play land {card_obj} from {from_zone.id}")
            return

        print(f"Player {self.id} playing land {card_obj}")
        battlefield = self.game.get_zone("battlefield")
        # Remove from hand first
        from_zone.remove(card_obj.id)
        # Then move the object representation
        card_obj.move_to_zone(battlefield, self.game)
        self.lands_played_this_turn += 1
        # TODO: Publish LandPlayedEvent
        # TODO: Pass priority back

    def take_special_action(self, action_type: str, source_id: Optional['ObjectId'] = None, options: 'SpecialActionOptions' = None) -> None:
        print(f"Warning: take_special_action {action_type} not implemented.")
        pass

    # --- Choices ---
    def make_choice(self, choice_type: str, options: 'ChoiceOptions', prompt: str) -> 'ChoiceResult':
        # Delegates to the input handler
        return self.input_handler.make_generic_choice(options, prompt)
        # Or call specific choice methods on input_handler

    def reset_turn_based_state(self) -> None:
        """Resets counters and states that refresh each turn."""
        self.lands_played_this_turn = 0
        # TODO: Reset other turn-based states if added
        print(f"Reset turn state for Player {self.id} (land drops: {self.lands_played_this_turn})")

    def __repr__(self) -> str:
        return f"Player<{self.id} ({self.life} life)>" 