"""Stub implementations for various interfaces, used when full functionality isn't needed."""
from typing import Callable, List, Dict, Any, Optional, TYPE_CHECKING

# Import base classes for stubs
from .events.base import Event
from .events.event_bus import EventBus
from .state.state_based_actions import StateBasedActionChecker
from .managers.effect_manager import EffectManager
from .effects.continuous import ContinuousEffect, ReplacementEffect, PreventionEffect
from .state.game_state import GameState
from .player.input_handler import PlayerInputHandler

if TYPE_CHECKING:
    from .game import Game
    from .game_objects.base import GameObject
    from .types import Targetable, CharacteristicsDict, ModeSelection, ChoiceOptions, ChoiceResult, ObjectId
    # Define placeholders
    class Mode: pass

# --- Stubs --- #

class StubEventBus(EventBus):
    """Event bus that does nothing or just prints."""
    def subscribe(self, event_type: str, callback: Callable[[Event], None]) -> None:
        # print(f"(StubEventBus) Subscribed to {event_type}")
        pass

    def publish(self, event: Event) -> None:
        print(f"(StubEventBus) Published: {event.event_type} - {event.__dict__}")
        pass

class StubSbaChecker(StateBasedActionChecker):
    """SBA checker that does nothing."""
    def check_and_perform(self, game: 'Game') -> bool:
        # print("(StubSbaChecker) Checking SBAs... none performed.")
        return False # Always returns False, no actions performed

class StubEffectManager(EffectManager):
    """Effect manager that provides only base characteristics."""
    def add_effect(self, effect: 'ContinuousEffect') -> None:
        # print(f"(StubEffectManager) Add effect: {effect}")
        pass

    def remove_effect(self, effect: 'ContinuousEffect') -> None:
        # print(f"(StubEffectManager) Remove effect: {effect}")
        pass

    def remove_expired_effects(self, game: 'Game') -> None:
        # print("(StubEffectManager) Removing expired effects...")
        pass

    def get_characteristics(self, obj: 'GameObject', game: 'Game') -> 'CharacteristicsDict':
        # print(f"(StubEffectManager) Getting characteristics for {obj.id}")
        # Returns only base characteristics, ignoring layers
        return obj.get_base_characteristics()

    def get_abilities(self, obj: 'GameObject', game: 'Game') -> List[Any]:
        # print(f"(StubEffectManager) Getting abilities for {obj.id}")
        # Returns only base abilities
        return obj.card_data.ability_definitions if obj.card_data else []

    def get_replacement_effects(self, event: Event, game: 'Game') -> List['ReplacementEffect']:
        return []

    def get_prevention_effects(self, damage_event: Event, game: 'Game') -> List['PreventionEffect']:
        return []

class StubGameState(GameState):
    """Minimal GameState stub."""
    # No state tracked for now
    pass

class AutoPlayerInputHandler(PlayerInputHandler):
    """Input handler that makes automatic choices for solitaire."""
    def __init__(self, player: 'Player', game: 'Game'):
        self.player = player
        self.game = game

    def choose_target(self, legal_targets: List['Targetable'], prompt: str) -> 'Targetable':
        print(f"(AutoInput) Choosing target: {prompt} - Selecting first: {legal_targets[0]}")
        return legal_targets[0] # Always choose the first legal target

    def choose_targets(self, legal_targets: List['Targetable'], num_targets: int, min_targets: int, prompt: str) -> List['Targetable']:
        print(f"(AutoInput) Choosing {num_targets} targets: {prompt} - Selecting first {num_targets}")
        return legal_targets[:num_targets]

    def choose_mode(self, legal_modes: List['Mode'], prompt: str) -> 'ModeSelection':
        print(f"(AutoInput) Choosing mode: {prompt} - Selecting first")
        return legal_modes[0] # Always choose the first mode

    def choose_yes_no(self, prompt: str) -> bool:
        print(f"(AutoInput) Choosing yes/no: {prompt} - Selecting Yes")
        return True # Always choose yes

    def choose_order(self, items: List[Any], prompt: str) -> List[Any]:
        print(f"(AutoInput) Choosing order: {prompt} - Keeping original")
        return items # Keep original order

    def choose_card_to_discard(self, hand: List['GameObject'], count: int, random: bool, prompt: str) -> List['GameObject']:
        print(f"(AutoInput) Choosing {count} card(s) to discard: {prompt} - Selecting first {count}")
        return hand[:count] # Discard the first cards

    def choose_distribution(self, total: int, categories: List[Any], prompt: str) -> Dict[Any, int]:
        print(f"(AutoInput) Choosing distribution: {prompt} - Distributing evenly/first")
        # Basic distribution: give all to the first category
        dist = {cat: 0 for cat in categories}
        if categories:
            dist[categories[0]] = total
        return dist

    def make_generic_choice(self, options: 'ChoiceOptions', prompt: str) -> 'ChoiceResult':
        """Handles generic choices, including passing priority or playing a land."""
        print(f"(AutoInput) Making generic choice: {prompt}")

        # --- Specific Logic for Solitaire Goal ---
        # Check if we can play a land
        hand_cards = self.player.get_hand().get_objects(self.game)
        playable_land = None
        for card in hand_cards:
            if self.player.can_play_land(card, self.player.get_hand()):
                playable_land = card
                break

        if playable_land:
            print(f"(AutoInput) Choice: Found playable land {playable_land}, choosing to play it.")
            # Returning the object signals the game loop to attempt playing it
            # (Alternative: Call player.play_land directly? Design choice.)
            return playable_land # Signal intent to play this land

        # --- Default Action: Pass Priority ---
        print("(AutoInput) Choice: No other actions available, choosing to pass priority.")
        # How to signal passing priority? Maybe return None or a specific sentinel value.
        # For now, assume returning None means pass.
        return None 