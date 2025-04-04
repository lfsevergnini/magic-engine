"""The main Game interface, orchestrating all components."""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .types import PlayerId, ObjectId, ZoneId, CardId, DeckDict
    from .player.player import Player
    from .zones.base import Zone
    from .zones.stack import Stack
    from .managers.turn_manager import TurnManager
    from .managers.priority_manager import PriorityManager
    from .managers.combat_manager import CombatManager
    from .managers.effect_manager import EffectManager
    from .state.state_based_actions import StateBasedActionChecker
    from .events.event_bus import EventBus
    from .state.game_state import GameState
    from .game_objects.base import GameObject
    from .game_objects.permanent import Permanent
    from .cards.card_data import CardData
    from .cards.token_data import TokenData
    from .enums import GameResult

class Game(ABC):
    """Central game orchestrator, holding references to all components and game state."""
    players: List['Player']
    zones: Dict['ZoneId', 'Zone'] # Shared zones (Battlefield, Stack, Exile, Command)
    turn_manager: 'TurnManager'
    priority_manager: 'PriorityManager'
    combat_manager: 'CombatManager'
    effect_manager: 'EffectManager'
    sba_checker: 'StateBasedActionChecker'
    event_bus: 'EventBus'
    game_state: 'GameState'
    objects: Dict['ObjectId', 'GameObject'] # Master registry of all in-game objects
    card_database: Dict['CardId', 'CardData'] # Loaded card definitions
    next_object_id: int = 0
    game_over: bool = False
    game_result: Optional[Tuple['GameResult', Optional['Player']]] = None

    @abstractmethod
    def start_game(self, decks: 'DeckDict') -> None:
        """Initializes the game state: creates players, zones, shuffles libraries, draws starting hands, etc."""
        pass

    @abstractmethod
    def run_main_loop(self) -> None:
        """Contains the core game loop: turn progression, priority passing, SBA checks, stack resolution."""
        pass

    @abstractmethod
    def resolve_top_stack_object(self) -> None:
        """Resolves the top spell or ability on the stack."""
        pass

    @abstractmethod
    def check_state_based_actions(self) -> bool:
        """Runs the SBA checker. Returns True if any actions were performed."""
        pass

    # --- Object/Player/Zone Accessors ---
    @abstractmethod
    def get_object(self, obj_id: 'ObjectId') -> Optional['GameObject']:
        """Retrieves a GameObject instance by its ID."""
        pass

    @abstractmethod
    def get_player(self, player_id: 'PlayerId') -> Optional['Player']:
        """Retrieves a Player instance by its ID."""
        pass

    @abstractmethod
    def get_zone(self, zone_id: 'ZoneId') -> Optional['Zone']:
        """Retrieves a Zone instance by its ID."""
        pass

    @abstractmethod
    def get_stack(self) -> 'Stack':
        """Convenience method to get the Stack zone."""
        pass

    # --- Object Creation/Registration ---
    @abstractmethod
    def register_object(self, obj: 'GameObject') -> None:
        """Adds a newly created GameObject to the master registry."""
        pass

    @abstractmethod
    def generate_object_id(self) -> 'ObjectId':
        """Generates a unique ID for a new GameObject."""
        pass

    @abstractmethod
    def create_token(self, token_data: 'TokenData', controller: 'Player') -> 'Permanent':
        """Creates a token permanent on the battlefield under the controller's control."""
        pass

    # --- Game End Conditions ---
    @abstractmethod
    def check_win_loss_condition(self) -> bool:
        """Checks if any win/loss conditions are met (player life, drawing from empty library, etc.). Returns True if game should end."""
        pass

    @abstractmethod
    def end_game(self, result: 'GameResult', winner: Optional['Player'] = None) -> None:
        """Sets the game result and stops the main loop."""
        pass 