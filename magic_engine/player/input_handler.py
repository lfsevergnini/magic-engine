"""Interface for abstracting player decisions."""
from abc import ABC, abstractmethod
from typing import List, Any, TYPE_CHECKING, Dict

if TYPE_CHECKING:
    # Use forward references (strings) or TYPE_CHECKING block
    from ..types import Targetable, ModeSelection, ChoiceOptions, ChoiceResult, ObjectId
    from ..game_objects.base import GameObject
    # from ..cards import Mode # Define Mode properly later
    class Mode:
        pass

class PlayerInputHandler(ABC):
    """Abstracts player decisions (human or AI)."""
    @abstractmethod
    def choose_target(self, legal_targets: List['Targetable'], prompt: str) -> 'Targetable':
        """Selects one target from a list."""
        pass

    @abstractmethod
    def choose_targets(self, legal_targets: List['Targetable'], num_targets: int, min_targets: int, prompt: str) -> List['Targetable']:
        """Selects a specific number of targets from a list."""
        pass

    @abstractmethod
    def choose_mode(self, legal_modes: List['Mode'], prompt: str) -> 'ModeSelection':
        """Selects a mode for a spell or ability."""
        pass

    @abstractmethod
    def choose_yes_no(self, prompt: str) -> bool:
        """Makes a boolean choice."""
        pass

    @abstractmethod
    def choose_order(self, items: List[Any], prompt: str) -> List[Any]:
        """Orders a list of items."""
        pass

    @abstractmethod
    def choose_card_to_discard(self, hand: List['GameObject'], count: int, random: bool, prompt: str) -> List['GameObject']:
        """Selects cards from hand to discard."""
        pass

    @abstractmethod
    def choose_distribution(self, total: int, categories: List[Any], prompt: str) -> Dict[Any, int]:
        """Distributes a total amount among categories (e.g., damage assignment, counter distribution)."""
        pass

    @abstractmethod
    def make_generic_choice(self, options: 'ChoiceOptions', prompt: str) -> 'ChoiceResult':
        """Handles generic choices not covered by other methods."""
        pass

    @abstractmethod
    def choose_action_with_priority(self, legal_actions: List[str], game_state_summary: str) -> str:
        """Chooses an action when the player has priority (e.g., 'play_land', 'tap_land', 'cast_spell', 'pass')."""
        pass

    # Add other necessary choice methods:
    # - choose_payment (for costs with options, e.g., hybrid mana)
    # - choose_replacement_effect_order
    # - choose_trigger_order
    # - choose_blockers
    # - choose_attacker_damage_assignment_order
    # - choose_blocker_damage_assignment_order

    # Add other necessary choice methods:
    # - choose_payment (for costs with options, e.g., hybrid mana)
    # - choose_replacement_effect_order
    # - choose_trigger_order
    # - choose_blockers
    # - choose_attacker_damage_assignment_order
    # - choose_blocker_damage_assignment_order 