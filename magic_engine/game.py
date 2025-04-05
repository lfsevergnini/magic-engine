"""The main Game interface, orchestrating all components."""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple, TYPE_CHECKING, Type

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
    from .enums import GameResult, CardType, StepType, PhaseType
    from .game_objects.concrete import ConcreteGameObject, ConcretePermanent

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
from magic_engine.constants import STARTING_HAND_SIZE
from .player.concrete_player import ConcretePlayer
from .player.cli_input_handler import CliInputHandler # Import CLI handler
from .stubs import StubEventBus, StubSbaChecker, StubEffectManager, StubGameState, AutoPlayerInputHandler # Re-import AutoPlayerInputHandler
from .managers.concrete_turn_manager import SimpleTurnManager
from .managers.concrete_priority_manager import SolitairePriorityManager, TwoPlayerPriorityManager
from .zones.concrete import Battlefield, ConcreteStack
from .game_objects.base import GameObject # Added runtime import
from .game_objects.concrete import ConcreteGameObject, ConcretePermanent
from .card_definitions.basic_lands import PlainsData, ForestData # Example card data
from .enums import GameResult, ZoneType, ManaType, CardType, StepType, PhaseType # Import PhaseType
import time # For timestamp

from .commands.base import ActionCommand
from .commands.pass_priority import PassPriorityCommand
from .commands.play_land import PlayLandCommand
from .commands.tap_land import TapLandCommand

# Import ZoneName constants if available (assuming they exist in enums or constants)
try:
    from .constants import ZoneId # Or from .enums import ZoneId
except ImportError:
    # Define simple string constants if not available
    class ZoneId:
        BATTLEFIELD = "battlefield"
        STACK = "stack"
        LIBRARY = "library"
        HAND = "hand"
        GRAVEYARD = "graveyard"
        EXILE = "exile"
        COMMAND = "command"


class ConcreteGame(Game):
    """Concrete implementation of the Game orchestrator."""
    def __init__(self):
        self.players: List['Player'] = []
        self.zones: Dict['ZoneId', 'Zone'] = {} # Shared zones only
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
        cards_to_load = [PlainsData, ForestData]
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
        num_players = len(decks)
        # --- Create Shared Zones ---
        battlefield = Battlefield() # ZoneId.BATTLEFIELD
        stack = ConcreteStack(zone_id=ZoneId.STACK)
        self.zones[ZoneId.BATTLEFIELD] = battlefield
        self.zones[ZoneId.STACK] = stack

        # --- Create Players and their Zones ---
        player_ids = list(decks.keys())
        if num_players == 1:
            player_id = player_ids[0]
            player = ConcretePlayer(player_id, self, None)
            handler = AutoPlayerInputHandler(player, self) # Solitaire uses Auto handler
            player.input_handler = handler
            self.players.append(player)
            print(f"Created Player {player.id} (Solitaire Mode) with zones: Library, Hand, Graveyard")
        elif num_players == 2:
            for player_id in player_ids:
                player = ConcretePlayer(player_id, self, None)
                handler = CliInputHandler(player, self) # Two-player uses CLI handler
                player.input_handler = handler
                self.players.append(player)
                print(f"Created Player {player.id} (Two-Player Mode) with zones: Library, Hand, Graveyard")
        else:
            raise ValueError(f"Unsupported number of players: {num_players}. Only 1 or 2 supported.")

        # --- Setup Managers ---
        # Determine starting player (e.g., randomly or fixed)
        starting_player_index = 0 # For simplicity, player 0 starts
        self.turn_manager = SimpleTurnManager(self.players, starting_player_index)
        if num_players == 1:
            self.priority_manager = SolitairePriorityManager()
        elif num_players == 2:
            self.priority_manager = TwoPlayerPriorityManager(self.players)
        print("Initialized Managers (Turn, Priority)")

        # --- Populate Library ---
        for player in self.players:
            deck_list = decks[player.id]
            library = player.get_library()
            print(f"Populating library for Player {player.id}...")
            for card_id_str in deck_list:
                card_data = self.card_database.get(card_id_str)
                if not card_data:
                    print(f"Warning: Card ID '{card_id_str}' not found in database for player {player.id}. Skipping.")
                    continue

                obj_id = self.generate_object_id()
                # Determine object type based on card type
                if any(pt in card_data.card_types for pt in [CardType.LAND, CardType.CREATURE, CardType.ARTIFACT, CardType.ENCHANTMENT, CardType.PLANESWALKER]):
                     game_obj_cls = ConcretePermanent
                     # Use 'zone' for ConcretePermanent
                     game_obj = game_obj_cls(self, obj_id, card_data, owner=player, controller=player, zone=library)
                else: # Instant, Sorcery, etc.
                     game_obj_cls = ConcreteGameObject
                     # Use 'initial_zone' for ConcreteGameObject
                     game_obj = game_obj_cls(self, obj_id, card_data, owner=player, controller=player, initial_zone=library)

                self.register_object(game_obj)
                library.add(obj_id, to_bottom=True)

            print(f"Library for Player {player.id} populated with {library.get_count()} cards.")
            library.shuffle()
            print(f"Library for Player {player.id} shuffled.")

        # --- Draw Starting Hand ---
        for player in self.players:
            print(f"Player {player.id} drawing initial hand ({STARTING_HAND_SIZE} cards)...")
            player.draw_cards(STARTING_HAND_SIZE)

        # --- Final Setup ---
        # Set initial player life (already done in Player constructor)
        # Active player is set by TurnManager init
        ap = self.turn_manager.current_turn_player()
        print(f"Starting player is {ap.id}")

        # Start the first turn explicitly
        self.turn_manager.start_turn(self)
        # Advance to Untap
        self.turn_manager.advance(self)
        # Advance to Upkeep to match test expectation
        self.turn_manager.advance(self)
        # self.turn_manager.advance(self) # Advance to Draw
        # self.turn_manager.advance(self) # Advance to Main

        print("===== Game Setup Complete ====")

    def get_object(self, obj_id: 'ObjectId') -> Optional['GameObject']:
        return self.objects.get(obj_id)

    def get_player(self, player_id: 'PlayerId') -> Optional['Player']:
        """Retrieves a Player instance by its ID."""
        for player in self.players:
            if player.id == player_id:
                return player
        return None

    def get_zone(self, zone_id: 'ZoneId') -> Optional['Zone']:
        """Retrieves a Zone instance by its ID. Checks shared zones first, then parses player-specific zone IDs (e.g., 'hand_0')."""
        # 1. Check shared zones (Battlefield, Stack, Exile, Command)
        if zone_id in self.zones:
            return self.zones[zone_id]

        # 2. Try parsing as a player-specific zone ID (e.g., "library_0")
        try:
            zone_type_str, player_id_str = zone_id.rsplit('_', 1)
            player_id = int(player_id_str) # Assuming player IDs are integers
        except (ValueError, AttributeError):
            # Cannot parse in the expected format
            print(f"Warning: Zone ID '{zone_id}' is not a shared zone and could not be parsed as player zone.")
            return None

        # 3. Map string to ZoneType enum
        zone_type_map = {
            "library": ZoneType.LIBRARY,
            "hand": ZoneType.HAND,
            "graveyard": ZoneType.GRAVEYARD,
            # Add other player-specific zones like command if needed
        }
        zone_type_enum = zone_type_map.get(zone_type_str.lower())

        if zone_type_enum is None:
            print(f"Warning: Unknown zone type '{zone_type_str}' in zone ID '{zone_id}'.")
            return None

        # 4. Find the player
        player = self.get_player(player_id)
        if player is None:
            print(f"Warning: Player with ID {player_id} not found for zone ID '{zone_id}'.")
            return None

        # 5. Access the player's zone dictionary
        player_zone = player.zones.get(zone_type_enum)

        if player_zone is None:
            # This indicates an internal inconsistency if the player exists
            print(f"Error: Player {player_id} found, but zone type {zone_type_enum.name} missing internally.")
        elif player_zone.id != zone_id:
            # Double-check the retrieved zone's ID matches the requested one
            print(f"Warning: Zone ID mismatch. Requested '{zone_id}', found zone with ID '{player_zone.id}'.")
            return None # Or return player_zone? Strict match seems safer.

        return player_zone

    def get_stack(self) -> 'ConcreteStack':
        # Need a concrete Stack implementation first
        stack = self.get_zone(ZoneId.STACK)
        if not isinstance(stack, ConcreteStack):
            raise TypeError(f"Expected ConcreteStack for zone '{ZoneId.STACK}', found {type(stack)}")
        return stack

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
                # Determine winner in 2-player game
                winner = None
                if len(self.players) == 2:
                     winner = next((p for p in self.players if p != player), None)
                # Assign loss/win based on context
                result = GameResult.LOSS if len(self.players) == 1 else GameResult.WIN # Solitaire loss, 2p win for opponent
                self.end_game(result, winner=winner)
                return True
            # TODO: Check drawing from empty library (might be handled in Player.draw)
            # TODO: Check poison counters
            # TODO: Check "Win the game" effects

        # --- Removed Solitaire Turn 1 End Condition ---
        # if self.turn_manager and self.turn_manager.turn_number > 1:
        #      print("Condition Met: Reached end of Turn 1.")
        #      self.end_game(GameResult.DRAW, winner=None) # End as Draw for test
        #      return True

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
        stack = self.get_stack()
        if not stack.is_empty():
            obj_id = stack.pop() # Assuming pop returns top object ID
            obj = self.get_object(obj_id)
            print(f"[Game Loop] Resolving {obj.name if obj else 'Unknown Object'} from stack...")
            # Actual resolution logic goes here
            # Need to handle moving card to graveyard if it was an Instant/Sorcery
            # Need to handle putting permanents onto battlefield
            # Need to execute effects
            # For now, just print
            # After resolution, check SBAs
            self.check_state_based_actions()
            # AP gets priority after resolution
            ap = self.turn_manager.current_turn_player()
            self.priority_manager.set_priority(ap)
        else:
            print("[Game Loop] Tried to resolve stack, but it was empty.")

    def check_state_based_actions(self) -> bool:
        # Delegates to the SBA checker
        # print("[Game Loop] Checking State-Based Actions...") # Can be verbose
        actions_performed = self.sba_checker.check_and_perform(self)
        # if actions_performed:
        #     print("[Game Loop] State-Based Actions were performed.")
        return actions_performed

    def _get_game_state_summary(self, player: 'Player') -> str:
        """Generates a string summary of the game state for the CLI, tailored to the given player."""
        opponent = next((p for p in self.players if p != player), None)
        active_player = self.turn_manager.current_turn_player()
        priority_player = self.priority_manager.get_current_player()
        battlefield = self.get_zone(ZoneId.BATTLEFIELD)

        lines = []
        lines.append("=" * 40)
        lines.append(f" Turn {self.turn_manager.turn_number} | {self.turn_manager.current_phase.name} Phase | {self.turn_manager.current_step.name} Step ")
        lines.append(f" Active Player: {active_player.id} {'(You)' if active_player == player else ''} ")
        lines.append(f" Priority: {priority_player.id if priority_player else 'None'} {'(You)' if priority_player == player else ''} ")
        lines.append("-" * 40)

        # Opponent Info
        if opponent:
            lines.append(f" Opponent (Player {opponent.id}):")
            lines.append(f"   Life: {opponent.life}")
            opponent_hand_count = opponent.get_hand().get_count()
            lines.append(f"   Hand: {opponent_hand_count} card(s)")
            opponent_library_count = opponent.get_library().get_count()
            lines.append(f"   Library: {opponent_library_count} card(s)")
            opp_perms = [p for p in battlefield.get_objects(self) if p.controller == opponent]
            opp_perms_str = [f"  {p.card_data.name} ({'Tapped' if p.is_tapped() else 'Untapped'})" 
                             for p in opp_perms if p.card_data]
            lines.append("   Battlefield:")
            if opp_perms_str:
                lines.extend(opp_perms_str)
            else:
                lines.append("     (Empty)")
            lines.append(f"   Mana Pool: {opponent.mana_pool}") # Display opponent mana
            lines.append("-" * 40)

        # Your Info
        lines.append(f" You (Player {player.id}):")
        lines.append(f"   Life: {player.life}")
        hand = player.get_hand()
        hand_cards = [f"{i+1}: {self.get_object(obj_id).card_data.name}" 
                      for i, obj_id in enumerate(hand.get_object_ids()) 
                      if self.get_object(obj_id) and self.get_object(obj_id).card_data]
        lines.append(f"   Hand ({hand.get_count()}): {', '.join(hand_cards) if hand_cards else '(Empty)'}")
        library_count = player.get_library().get_count()
        lines.append(f"   Library: {library_count} card(s)")
        my_perms = [p for p in battlefield.get_objects(self) if p.controller == player]
        # Include index for selection later
        my_perms_str = [f"  {i+1}: {p.card_data.name} ({'Tapped' if p.is_tapped() else 'Untapped'})" 
                        for i, p in enumerate(my_perms) if p.card_data]
        lines.append("   Battlefield:")
        if my_perms_str:
            lines.extend(my_perms_str)
        else:
            lines.append("     (Empty)")
        lines.append(f"   Mana Pool: {player.mana_pool}")
        lines.append("=" * 40)

        return "\n".join(lines)

    def _get_legal_actions(self, player: 'Player') -> List[ActionCommand]:
        """Determines the legal actions (as command objects) a player can take."""
        actions: List[ActionCommand] = []

        # Always possible to pass when holding priority
        if PassPriorityCommand.is_legal(self, player):
            actions.append(PassPriorityCommand())

        # Check playing a land
        if PlayLandCommand.is_legal(self, player):
            # We could potentially create specific commands for each land card here,
            # e.g., PlayLandCommand(land_card_object), but for now, a generic one
            # that prompts the user inside execute() is simpler.
             actions.append(PlayLandCommand())

        # Check tapping lands for mana
        if TapLandCommand.is_legal(self, player):
            # Similar to playing land, we could generate specific commands per land,
            # e.g., TapLandCommand(land_permanent_object), but a generic one works.
             actions.append(TapLandCommand())

        # TODO: Add checks for casting spells, activating abilities, etc.
        # Example:
        # if CastSpellCommand.is_legal(self, player):
        #     # Find castable spells in hand and generate commands
        #     hand_cards = [...]
        #     for card in hand_cards:
        #         if CastSpellCommand.can_cast(self, player, card):
        #             actions.append(CastSpellCommand(card))
        # if ActivateAbilityCommand.is_legal(self, player):
        #     # Find permanents with activatable abilities
        #     permanents = [...]
        #     for perm in permanents:
        #         for ability in perm.get_activatable_abilities():
        #              if ability.can_activate(self, player):
        #                   actions.append(ActivateAbilityCommand(ability))


        return actions

    def _execute_action(self, player: 'Player', command: ActionCommand) -> None:
        """Executes the chosen ActionCommand."""
        print(f"[Game Loop] Player {player.id} chose action: {command.get_display_name()}")
        # The command object itself now handles the execution logic
        command.execute(self, player)

    def run_main_loop(self) -> None:
        """Contains the core game loop: turn progression, priority passing, SBA checks, stack resolution."""
        print("\n===== Starting Main Game Loop =====")
        while not self.game_over:
            # Check Win/Loss Conditions first
            if self.check_win_loss_condition():
                # end_game should set self.game_over
                break

            # Perform State-Based Actions repeatedly until none occur
            # while self.check_state_based_actions():
            #     pass # Keep checking until stable
            # Run SBAs once per loop iteration for now, or after specific events
            self.check_state_based_actions() 

            player_with_priority = self.priority_manager.get_current_player()

            if player_with_priority:
                # Player has priority, get their action
                game_summary = self._get_game_state_summary(player_with_priority)
                # Now gets a list of ActionCommand objects
                legal_actions: List[ActionCommand] = self._get_legal_actions(player_with_priority)

                # Use the player's input handler - IT MUST NOW HANDLE ActionCommand objects
                chosen_command: Optional[ActionCommand] = player_with_priority.input_handler.choose_action_with_priority(
                    legal_actions, game_summary
                )

                # Execute the action command object
                if chosen_command:
                    self._execute_action(player_with_priority, chosen_command)
                else:
                    # Handle cases where input handler returns None (e.g., user quits)
                    print("[Game Loop] No action chosen. Passing priority by default.")
                    PassPriorityCommand().execute(self, player_with_priority) # Default to pass

            else:
                # No player has priority, check if stack resolves or turn advances
                if self.priority_manager.check_stack_resolve(self):
                    # Both players passed in succession
                    stack = self.get_stack()
                    if stack.is_empty():
                        # Stack is empty, advance to next step/phase
                        print("[Game Loop] Both players passed on empty stack. Advancing turn.")
                        self.turn_manager.advance(self)
                        # Active player gets priority (handled in turn_manager.advance)
                    else:
                        # Stack is not empty, resolve the top object
                        print("[Game Loop] Both players passed. Resolving top stack object.")
                        self.resolve_top_stack_object()
                        # Priority is set after resolution within resolve_top_stack_object
                else:
                    # This state should ideally not be reached if priority logic is correct
                    # (Either someone has priority, or check_stack_resolve should be true)
                    print("[Game Loop] Warning: No priority, but stack not resolving. Check logic.")
                    # Maybe force advance turn? Or set priority to AP?
                    # For now, let's give priority back to Active Player to avoid getting stuck
                    ap = self.turn_manager.current_turn_player()
                    self.priority_manager.set_priority(ap)
                    time.sleep(1) # Pause briefly to avoid spamming warnings

            # Optional: Add a small delay for readability in CLI
            # time.sleep(0.1)

        # Game Over
        print("\n===== Game Over =====")
        if self.game_result:
            result_type, winner = self.game_result
            if winner:
                print(f"Result: {result_type.name}, Winner: Player {winner.id}")
            else:
                print(f"Result: {result_type.name} (Draw)")
        else:
            print("Result: Unknown (Game ended abruptly)")


    # ... [rest of ConcreteGame] ... 