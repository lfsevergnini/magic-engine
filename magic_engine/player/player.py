"""Interface representing a player in the game."""
from abc import ABC, abstractmethod
from typing import Dict, Optional, TYPE_CHECKING, List, Any

if TYPE_CHECKING:
    from ..types import PlayerId, ObjectId, CountersDict, SpellCastingOptions, AbilityActivationOptions, SpecialActionOptions, ChoiceOptions, ChoiceResult
    from ..enums import CounterType, ZoneType
    from ..player.mana_pool import ManaPool
    from ..zones.base import Zone
    from ..player.input_handler import PlayerInputHandler
    from ..costs.base import Cost
    from ..game_objects.base import GameObject
    from ..game import Game

class Player(ABC):
    """Represents a player in the Magic: The Gathering game."""
    id: 'PlayerId'
    life: int
    mana_pool: 'ManaPool'
    zones: Dict['ZoneType', 'Zone'] # Owns Library, Hand, Graveyard
    counters: 'CountersDict' # e.g., Poison, Energy
    game: 'Game' # Reference back to the main game object
    input_handler: 'PlayerInputHandler' # Handles choices for this player

    # --- Player State Attributes ---
    has_priority: bool = False
    has_lost: bool = False
    has_won: bool = False
    lands_played_this_turn: int = 0
    # Add other state: mulligan status, spells cast this turn, life lost/gained this turn, etc.

    @abstractmethod
    def draw_cards(self, number: int) -> None:
        """Moves the specified number of cards from the player's library to their hand."""
        pass

    @abstractmethod
    def lose_life(self, amount: int, source_id: Optional['ObjectId'] = None) -> None:
        """Reduces the player's life total."""
        pass

    @abstractmethod
    def gain_life(self, amount: int, source_id: Optional['ObjectId'] = None) -> None:
        """Increases the player's life total."""
        pass

    @abstractmethod
    def can_pay_cost(self, cost: 'Cost', source: 'GameObject') -> bool:
        """Checks if the player has the necessary resources (mana, life, permanents to tap/sac) to pay a cost."""
        pass

    @abstractmethod
    def pay_cost(self, cost: 'Cost', source: 'GameObject') -> None:
        """Pays the specified cost."""
        pass

    # --- Actions --- (Checking Legality)
    @abstractmethod
    def can_cast(self, card_obj: 'GameObject', from_zone: 'Zone') -> bool:
        """Checks if the player can legally cast the given spell card from the specified zone (timing, permissions, costs)."""
        pass

    @abstractmethod
    def can_activate(self, ability_source: 'GameObject', ability_index: int) -> bool:
        """Checks if the player can legally activate the specified ability (timing, permissions, costs)."""
        pass

    @abstractmethod
    def can_play_land(self, card_obj: 'GameObject', from_zone: 'Zone') -> bool:
        """Checks if the player can legally play the given land card from the specified zone (timing, land drop limit)."""
        pass

    # --- Actions --- (Performing)
    @abstractmethod
    def cast_spell(self, card_obj: 'GameObject', from_zone: 'Zone', options: 'SpellCastingOptions') -> None:
        """Initiates the process of casting a spell: moving to stack, choosing modes/targets, paying costs."""
        pass

    @abstractmethod
    def activate_ability(self, ability_source: 'GameObject', ability_index: int, options: 'AbilityActivationOptions') -> None:
        """Initiates the process of activating an ability: putting on stack, choosing modes/targets, paying costs."""
        pass

    @abstractmethod
    def play_land(self, card_obj: 'GameObject', from_zone: 'Zone') -> None:
        """Plays a land card directly onto the battlefield."""
        pass

    @abstractmethod
    def take_special_action(self, action_type: str, source_id: Optional['ObjectId'] = None, options: 'SpecialActionOptions' = None) -> None:
        """Performs a special action that doesn't use the stack (e.g., turning face-down creature up, playing suspend card)."""
        pass

    # --- Choices ---
    @abstractmethod
    def make_choice(self, choice_type: str, options: 'ChoiceOptions', prompt: str) -> 'ChoiceResult':
        """Delegates making a decision to the player's input_handler."""
        pass 