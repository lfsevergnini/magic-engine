"""Unit tests for the solitaire game scenario."""
import unittest
import random

# # Adjust path to import from the parent directory (magic_engine)
# # This ensures the test runner can find the 'magic_engine' package
# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.dirname(current_dir)
# sys.path.insert(0, parent_dir) # Removed this block

from magic_engine.game import ConcreteGame
from magic_engine.game_objects.concrete import ConcretePermanent
from magic_engine.enums import PhaseType, StepType, ZoneType, ManaType, StatusType, GameResult, CardType
from magic_engine.abilities.mana_ability import TapManaAbility
from magic_engine.types import DeckDict, PlayerId
from magic_engine.constants import STARTING_HAND_SIZE, STARTING_LIBRARY_SIZE

# Suppress print statements during tests for cleaner output
# Comment this out if you want to see the game's print statements
import builtins
_original_print = builtins.print
def muted_print(*args, **kwargs):
    pass
# builtins.print = muted_print

class TestSolitaireTurn(unittest.TestCase):
    """Tests the basic solitaire turn: setup, draw, play land, mana, end."""

    def setUp(self):
        """Set up a new game instance for each test."""
        # Seed the random number generator for deterministic shuffling during tests
        random.seed(42) # Use a fixed seed

        # Suppress prints for setup
        # old_print = builtins.print
        # builtins.print = muted_print

        self.game = ConcreteGame()
        self.player_id: PlayerId = 0
        # Deck consists of 60 Plains cards
        self.deck: DeckDict = {self.player_id: ["plains_basic"] * STARTING_LIBRARY_SIZE}
        self.game.start_game(self.deck)
        self.player = self.game.get_player(self.player_id)

        # Restore print function if it was muted
        # builtins.print = old_print

        # Ensure setup finished correctly
        self.assertIsNotNone(self.player)
        self.assertEqual(len(self.game.players), 1)
        self.assertEqual(self.player.get_library().get_count(), STARTING_LIBRARY_SIZE - STARTING_HAND_SIZE)
        self.assertEqual(self.player.get_hand().get_count(), STARTING_HAND_SIZE)
        self.assertEqual(self.game.turn_manager.turn_number, 1)
        # start_game advances to upkeep automatically
        self.assertEqual(self.game.turn_manager.current_phase, PhaseType.BEGINNING)
        self.assertEqual(self.game.turn_manager.current_step, StepType.UPKEEP)

    def tearDown(self):
        """Restore print function after each test."""
        builtins.print = _original_print

    def test_01_phase_progression(self):
        """Test advancing through the steps of the first turn."""
        tm = self.game.turn_manager

        # Currently at Upkeep
        self.assertEqual(tm.current_step, StepType.UPKEEP)
        tm.advance(self.game)
        self.assertEqual(tm.current_phase, PhaseType.BEGINNING)
        self.assertEqual(tm.current_step, StepType.DRAW)
        # Player should have drawn a card
        self.assertEqual(self.player.get_hand().get_count(), STARTING_HAND_SIZE + 1)

        tm.advance(self.game)
        self.assertEqual(tm.current_phase, PhaseType.PRECOMBAT_MAIN)
        self.assertEqual(tm.current_step, StepType.MAIN)

        tm.advance(self.game)
        self.assertEqual(tm.current_phase, PhaseType.COMBAT)
        self.assertEqual(tm.current_step, StepType.BEGIN_COMBAT)

        tm.advance(self.game)
        self.assertEqual(tm.current_phase, PhaseType.COMBAT)
        self.assertEqual(tm.current_step, StepType.DECLARE_ATTACKERS)

        tm.advance(self.game)
        self.assertEqual(tm.current_phase, PhaseType.COMBAT)
        self.assertEqual(tm.current_step, StepType.DECLARE_BLOCKERS)

        tm.advance(self.game)
        self.assertEqual(tm.current_phase, PhaseType.COMBAT)
        self.assertEqual(tm.current_step, StepType.COMBAT_DAMAGE)

        tm.advance(self.game)
        self.assertEqual(tm.current_phase, PhaseType.COMBAT)
        self.assertEqual(tm.current_step, StepType.END_OF_COMBAT)

        tm.advance(self.game)
        self.assertEqual(tm.current_phase, PhaseType.POSTCOMBAT_MAIN)
        self.assertEqual(tm.current_step, StepType.MAIN)

        tm.advance(self.game)
        self.assertEqual(tm.current_phase, PhaseType.ENDING)
        self.assertEqual(tm.current_step, StepType.END)

        tm.advance(self.game)
        self.assertEqual(tm.current_phase, PhaseType.ENDING)
        self.assertEqual(tm.current_step, StepType.CLEANUP)
        # Mana pool should be empty after cleanup
        self.assertEqual(self.player.mana_pool.get_amount(ManaType.WHITE), 0)

    def test_02_play_land(self):
        """Test playing a land using the game loop and AutoPlayerInputHandler."""
        tm = self.game.turn_manager
        # Game setup puts us in Upkeep. Advance to Draw, then Main.
        tm.advance(self.game) # -> Draw
        tm.advance(self.game) # -> Main
        self.assertEqual(tm.current_phase, PhaseType.PRECOMBAT_MAIN)
        self.assertEqual(tm.current_step, StepType.MAIN)
        
        # State before playing land
        self.assertEqual(self.player.lands_played_this_turn, 0)
        hand = self.player.get_hand()
        initial_hand_count = hand.get_count() # Should be 8 after draw
        self.assertEqual(initial_hand_count, 8)
        battlefield = self.game.get_zone("battlefield")
        self.assertIsNotNone(battlefield, "Battlefield zone should exist")
        initial_bf_count = battlefield.get_count() # Should be 0

        # Simulate one iteration of the game loop where player has priority
        player_with_priority = self.game.priority_manager.get_current_player()
        self.assertEqual(player_with_priority, self.player, "Player should have priority in their main phase")

        if player_with_priority:
            # Get action from AutoInputHandler
            game_summary = self.game._get_game_state_summary(player_with_priority)
            legal_actions = self.game._get_legal_actions(player_with_priority)
            self.assertIn("play_land", legal_actions, "play_land should be a legal action")

            chosen_action = player_with_priority.input_handler.choose_action_with_priority(
                legal_actions, game_summary
            )
            self.assertEqual(chosen_action, "play_land", "AutoInputHandler should choose to play land")

            # Execute the action using the game's method
            print(f"Test: Executing action '{chosen_action}' for player {player_with_priority.id}")
            self.game._execute_action(player_with_priority, chosen_action)
        else:
            self.fail("No player had priority when expected")

        # Check state *after* the action is executed
        self.assertEqual(self.player.lands_played_this_turn, 1, "Land drop count should be 1")
        self.assertEqual(battlefield.get_count(), initial_bf_count + 1, "Battlefield count should increase by 1")
        self.assertEqual(hand.get_count(), initial_hand_count - 1, "Hand count should decrease by 1")
        # Verify the specific land moved (find the land on battlefield)
        bf_objs = battlefield.get_objects(self.game)
        self.assertTrue(any(obj.card_data and CardType.LAND in obj.card_data.card_types for obj in bf_objs), "A land should be on the battlefield")

    def test_03_tap_land_for_mana(self):
        """Test tapping the played land for mana using the game loop."""
        tm = self.game.turn_manager
        bf = self.game.get_zone("battlefield")
        self.assertIsNotNone(bf, "Battlefield zone should exist")

        # Advance to Main Phase
        tm.advance(self.game) # Draw
        tm.advance(self.game) # Main

        # --- Simulate Playing the Land --- 
        player_with_priority = self.game.priority_manager.get_current_player()
        self.assertEqual(player_with_priority, self.player)
        game_summary = self.game._get_game_state_summary(player_with_priority)
        legal_actions = self.game._get_legal_actions(player_with_priority)
        chosen_action = player_with_priority.input_handler.choose_action_with_priority(legal_actions, game_summary)
        self.assertEqual(chosen_action, "play_land")
        self.game._execute_action(player_with_priority, chosen_action)
        # --- Land Played --- 

        self.assertEqual(bf.get_count(), 1)
        land_obj = bf.get_objects(self.game)[0]
        self.assertFalse(land_obj.is_tapped(), "Land should enter untapped")
        initial_mana = self.player.mana_pool.get_amount(ManaType.WHITE)

        # --- Simulate Tapping the Land --- 
        # Player should still have priority after playing land
        player_with_priority = self.game.priority_manager.get_current_player()
        self.assertEqual(player_with_priority, self.player)
        
        if player_with_priority:
            game_summary = self.game._get_game_state_summary(player_with_priority)
            legal_actions = self.game._get_legal_actions(player_with_priority)
            self.assertNotIn("play_land", legal_actions, "Cannot play another land")
            self.assertIn("tap_land", legal_actions, "tap_land should be a legal action")

            chosen_action = player_with_priority.input_handler.choose_action_with_priority(
                legal_actions, game_summary
            )
            # AutoInputHandler prefers play_land, then tap_land
            self.assertEqual(chosen_action, "tap_land", "AutoInputHandler should choose to tap land")

            # Execute the action
            print(f"Test: Executing action '{chosen_action}' for player {player_with_priority.id}")
            self.game._execute_action(player_with_priority, chosen_action)
        else:
             self.fail("No player had priority when expected")

        # --- Land Tapped --- 

        # Check state *after* tapping
        self.assertTrue(land_obj.is_tapped(), "Land should now be tapped")
        self.assertEqual(self.player.mana_pool.get_amount(ManaType.WHITE), initial_mana + 1, "Mana pool should have 1 white mana")

        # Try getting actions again (should not include tap_land for the tapped land)
        player_with_priority = self.game.priority_manager.get_current_player()
        self.assertEqual(player_with_priority, self.player) # Still has priority
        legal_actions = self.game._get_legal_actions(player_with_priority)
        self.assertNotIn("tap_land", legal_actions, "tap_land should not be legal for tapped land")
        self.assertIn("pass", legal_actions)

if __name__ == '__main__':
    # To run tests easily: python -m unittest tests/test_solitaire_turn.py
    unittest.main() 