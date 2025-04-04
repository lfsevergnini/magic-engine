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
    from .enums import GameResult, CardType, StepType

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

# --- Concrete Implementation ---

# Import concrete components and stubs
from .player.concrete_player import ConcretePlayer
from .player.input_handler import PlayerInputHandler # For type hint
from .stubs import AutoPlayerInputHandler, StubEventBus, StubSbaChecker, StubEffectManager, StubGameState
from .managers.concrete_turn_manager import SimpleTurnManager
from .managers.concrete_priority_manager import SolitairePriorityManager
from .zones.concrete import Battlefield, Stack # Concrete zones
from .game_objects.concrete import ConcreteGameObject, ConcretePermanent
from .card_definitions.basic_lands import PlainsData, ForestData # Example card data
from .enums import GameResult, ZoneType, ManaType
import time # For timestamp


class ConcreteGame(Game):
    """Concrete implementation of the Game orchestrator."""
    def __init__(self):
        self.players: List['Player'] = []
        self.zones: Dict['ZoneId', 'Zone'] = {}
        self.objects: Dict['ObjectId', 'GameObject'] = {}
        self.card_database: Dict['CardId', 'CardData'] = {}
        self.next_object_id: int = 0
        self._next_timestamp: int = 0
        self.game_over: bool = False
        self.game_result: Optional[Tuple['GameResult', Optional['Player']]] = None

        # Initialize core components (stubs and simple versions for now)
        self.event_bus: 'EventBus' = StubEventBus()
        self.sba_checker: 'StateBasedActionChecker' = StubSbaChecker()
        self.effect_manager: 'EffectManager' = StubEffectManager()
        self.game_state: 'GameState' = StubGameState()
        self.combat_manager = None # Not needed for this scenario yet

        # Priority and Turn managers will be set during start_game based on players
        self.turn_manager: Optional['TurnManager'] = None
        self.priority_manager: Optional['PriorityManager'] = None

        # Load basic cards into database
        self._load_card_database()

    def _load_card_database(self):
        """Loads card definitions into the database. Hardcoded for now."""
        print("Loading card database...")
        cards_to_load = [PlainsData(), ForestData()] # Add SavannahLionsData, GrizzlyBearsData later if needed
        for card_data in cards_to_load:
            self.card_database[card_data.id] = card_data
            print(f"  Loaded: {card_data.name} ({card_data.id})")
        print(f"Card database loaded with {len(self.card_database)} cards.")

    def generate_object_id(self) -> 'ObjectId':
        """Generates a unique ID for a new GameObject."""
        new_id = self.next_object_id
        self.next_object_id += 1
        return new_id

    def generate_timestamp(self) -> int:
        """Generates a unique timestamp."""
        # Simple counter is fine for now, real system might use more complex logic
        ts = self._next_timestamp
        self._next_timestamp += 1
        return ts

    def register_object(self, obj: 'GameObject') -> None:
        """Adds a GameObject to the master registry."""
        if obj.id in self.objects:
            print(f"Warning: Object ID {obj.id} already exists. Overwriting.")
        self.objects[obj.id] = obj

    def start_game(self, decks: 'DeckDict') -> None:
        """Initializes the game state for the solitaire scenario."""
        print("\n===== Starting Game Setup =====")
        if len(decks) != 1:
            raise ValueError("This setup currently supports only one player.")

        # --- Create Shared Zones ---
        battlefield = Battlefield()
        stack = Stack(zone_id="stack") # Need concrete Stack later
        self.zones[battlefield.id] = battlefield
        self.zones[stack.id] = stack

        # --- Create Player ---
        player_id, deck_list = list(decks.items())[0]
        # Create the auto-input handler first, player needs it
        # Need to handle the case where player is not yet created for input handler init
        temp_player_ref = {"player": None} # Use a mutable container
        auto_input_handler = AutoPlayerInputHandler(temp_player_ref, self)
        player = ConcretePlayer(player_id, self, auto_input_handler)
        temp_player_ref["player"] = player # Now set the player reference in the handler
        self.players.append(player)

        print(f"Created Player {player.id}")

        # --- Setup Managers ---
        self.turn_manager = SimpleTurnManager(starting_player=player)
        self.priority_manager = SolitairePriorityManager()
        print("Initialized Managers (Turn, Priority)")

        # --- Populate Library ---
        library = player.get_library()
        print(f"Populating library for Player {player.id}...")
        for card_id_str in deck_list:
            card_data = self.card_database.get(card_id_str)
            if not card_data:
                print(f"Warning: Card ID '{card_id_str}' not found in database. Skipping.")
                continue

            obj_id = self.generate_object_id()
            # Create the base object first (representing the card)
            # It starts conceptually "outside the game" then moves to the library
            game_obj = ConcreteGameObject(self, obj_id, card_data, owner=player, controller=player, zone=None) # Zone set by move
            self.register_object(game_obj)
            # Add ID to library zone list (object is moved implicitly)
            library.add(obj_id, to_bottom=True) # Add to bottom before shuffle

        print(f"Library populated with {library.get_count()} cards.")
        library.shuffle()
        print("Library shuffled.")

        # --- Draw Starting Hand ---
        print(f"Player {player.id} drawing initial hand (7 cards)...")
        player.draw_cards(7)

        # --- Final Setup ---
        # Set initial player life (already done in Player constructor)
        # Determine starting player (already done in TurnManager constructor)
        # Apply mulligans (TODO)

        # Start the first turn explicitly
        self.turn_manager.start_turn(self)
        # Advance to the first step where priority is given (Upkeep)
        self.turn_manager.advance(self)
        # self.turn_manager.advance(self) # Advance to Draw
        # self.turn_manager.advance(self) # Advance to Main

        print("===== Game Setup Complete ====")

    def get_object(self, obj_id: 'ObjectId') -> Optional['GameObject']:
        return self.objects.get(obj_id)

    def get_player(self, player_id: 'PlayerId') -> Optional['Player']:
        # Simple linear search for one player
        for p in self.players:
            if p.id == player_id:
                return p
        return None

    def get_zone(self, zone_id: 'ZoneId') -> Optional['Zone']:
        # Check player zones first, then shared zones
        for p in self.players:
            for zone in p.zones.values():
                if zone.id == zone_id:
                    return zone
        return self.zones.get(zone_id)

    def get_stack(self) -> 'Stack':
        # Need a concrete Stack implementation first
        stack_zone = self.zones.get("stack")
        if isinstance(stack_zone, Stack):
            return stack_zone
        else:
            # This should not happen if setup is correct
            raise TypeError("Stack zone is not of type Stack!")

    def create_token(self, token_data: 'TokenData', controller: 'Player') -> 'Permanent':
        # TODO: Implement token creation
        print(f"Warning: create_token for {token_data.name} not implemented.")
        # Basic implementation:
        obj_id = self.generate_object_id()
        battlefield = self.get_zone('battlefield')
        # Note: Tokens need a ConcretePermanent representation
        token_perm = ConcretePermanent(self, obj_id, token_data, owner=controller, controller=controller, zone=battlefield)
        self.register_object(token_perm)
        battlefield.add(token_perm.id)
        print(f"Created token {token_perm}")
        return token_perm

    def check_win_loss_condition(self) -> bool:
        """Checks basic win/loss conditions (life total)."""
        if self.game_over:
            return True

        for player in self.players:
            if player.life <= 0:
                print(f"Condition Met: Player {player.id} has {player.life} life.")
                # In solitaire, this is a loss
                self.end_game(GameResult.LOSS, winner=None)
                return True
            # TODO: Check drawing from empty library (might be handled in Player.draw)
            # TODO: Check poison counters
            # TODO: Check "Win the game" effects

        # For solitaire test, end after Turn 1 Cleanup
        if self.turn_manager and self.turn_manager.turn_number > 1:
             print("Condition Met: Reached end of Turn 1.")
             self.end_game(GameResult.DRAW, winner=None) # End as Draw for test
             return True

        return False

    def end_game(self, result: 'GameResult', winner: Optional['Player'] = None) -> None:
        if not self.game_over:
            print(f"\n===== GAME OVER =====")
            print(f"Result: {result.name}")
            if winner:
                print(f"Winner: Player {winner.id}")
            self.game_over = True
            self.game_result = (result, winner)

    def resolve_top_stack_object(self) -> None:
        # TODO: Implement stack resolution
        print("Warning: resolve_top_stack_object not implemented.")
        # stack = self.get_stack()
        # obj_id = stack.pop()
        # if obj_id:
        #     stack_obj = self.get_object(obj_id)
        #     if stack_obj and hasattr(stack_obj, 'resolve'):
        #          print(f"Resolving {stack_obj}...")
        #          stack_obj.resolve(self)
        #          # Check SBAs immediately after resolution
        #          while self.check_state_based_actions():
        #               pass # Keep checking until no more SBAs happen
        #     else:
        #          print(f"Error: Could not find or resolve object {obj_id} from stack.")
        pass

    def check_state_based_actions(self) -> bool:
        # Delegates to the SBA checker
        return self.sba_checker.check_and_perform(self)

    # --- Main Game Loop --- (Simplified for Solitaire)
    def run_main_loop(self) -> None:
        """Core game loop for the solitaire scenario."""
        print("\n===== Running Main Game Loop ====")
        while not self.game_over:
            # 1. Check State-Based Actions (SBAs)
            # Loop SBAs until none are performed
            while self.check_state_based_actions():
                if self.game_over: break # SBAs might cause game end
            if self.game_over: break

            # 2. Check for Win/Loss Conditions (redundant check after SBAs?)
            if self.check_win_loss_condition():
                 break

            # 3. Check Triggers (TODO)
            # If triggers occurred, put them on stack, players get priority.

            # 4. Priority Handling
            current_player = self.priority_manager.get_current_player()
            if current_player:
                # Player has priority, get their action
                print(f"Player {current_player.id} has priority ({self.turn_manager.current_phase.name} - {self.turn_manager.current_step.name}). Waiting for action...")
                # Use the InputHandler to get the action
                # For AutoPlayerInputHandler, this simulates the choice
                action_choice = current_player.make_choice("main_action", [], "Choose action or pass")

                if action_choice is None:
                    # Player chose to pass
                    self.priority_manager.pass_priority(current_player, self)
                elif isinstance(action_choice, GameObject) and action_choice.card_data and CardType.LAND in action_choice.card_data.card_types:
                     # Player chose to play a land (signaled by returning the object)
                     print(f"Attempting action: Play Land {action_choice}")
                     current_player.play_land(action_choice, current_player.get_hand())
                     # Playing a land doesn't use the stack, player retains priority (usually)
                     # For simplicity, let's assume they pass after playing land here.
                     # A real loop would re-prompt for action.
                     self.priority_manager.pass_priority(current_player, self)
                else:
                    # TODO: Handle other actions (casting spells, activating abilities)
                    print(f"Warning: Unknown action choice from player {current_player.id}: {action_choice}. Passing.")
                    self.priority_manager.pass_priority(current_player, self)

            else:
                # No player has priority. Check if stack needs resolving or turn advances.
                if not self.get_stack().is_empty():
                    if self.priority_manager.check_stack_resolve(self):
                        print("All players passed. Resolving top stack object.")
                        self.resolve_top_stack_object()
                        # After resolution, active player usually gets priority again
                        # self.priority_manager.set_priority(self.turn_manager.current_turn_player())
                    else:
                        # Should not happen in solitaire if priority logic is correct
                        print("Warning: No priority, but stack not resolving?")
                        # Force advance for testing
                        self.turn_manager.advance(self)

                else:
                     # Stack is empty, no one has priority. Check if turn should advance.
                     if self.priority_manager.check_stack_resolve(self):
                         print("Stack empty, all players passed. Advancing turn.")
                         self.turn_manager.advance(self)
                     else:
                         # This state might occur during steps without priority (Untap, Cleanup)
                         # Or if priority should have been assigned but wasn't
                         # print("Warning: No priority, stack empty, not resolving?")
                         # Force advance if stuck (e.g. after cleanup)
                         if self.turn_manager.current_step in [StepType.UNTAP, StepType.CLEANUP]:
                              self.turn_manager.advance(self)
                         else:
                              # Assign priority if we are in a step that should have it
                              print("State Error Recovery: Assigning priority to active player.")
                              self.priority_manager.set_priority(self.turn_manager.current_turn_player())

        print("===== Main Game Loop Ended ====") 