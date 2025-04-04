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
        """Test automatically playing a land during the main phase."""
        # Game setup puts us in Upkeep. Advance to Draw, then Main.
        self.game.turn_manager.advance(self.game) # -> Draw
        self.assertEqual(self.game.turn_manager.current_step, StepType.DRAW)
        self.game.turn_manager.advance(self.game) # -> Main
        self.assertEqual(self.game.turn_manager.current_phase, PhaseType.PRECOMBAT_MAIN)
        self.assertEqual(self.game.turn_manager.current_step, StepType.MAIN)
        
        # State before playing land
        self.assertEqual(self.player.lands_played_this_turn, 0, "Land drop should be available")
        hand = self.player.get_hand()
        initial_hand_count = hand.get_count() # Should be 8 after draw step
        self.assertEqual(initial_hand_count, 8, "Hand should have 8 cards after draw")
        battlefield = self.game.get_zone("battlefield")
        initial_bf_count = battlefield.get_count() # Should be 0

        # Simulate getting priority and making the choice
        # AutoPlayerInputHandler should choose to play a land
        self.game.priority_manager.set_priority(self.player) # Ensure player has priority
        action_choice = self.player.make_choice("main_action", [], "Choose action or pass")

        # Verify the choice was a land object from hand
        self.assertIsInstance(action_choice, ConcretePermanent, "Action choice should be a Permanent")
        self.assertIn(CardType.LAND, action_choice.card_data.card_types, "Chosen object should be a Land")
        self.assertTrue(hand.contains(action_choice.id), "Chosen land should be in hand initially")
        
        # Manually execute the play_land action
        print(f"Test: Manually playing land {action_choice}")
        self.player.play_land(action_choice, hand)

        # Check state *immediately after* playing the land
        self.assertEqual(self.player.lands_played_this_turn, 1, "Land drop count should be 1")
        self.assertEqual(battlefield.get_count(), initial_bf_count + 1, "Battlefield count should increase by 1")
        self.assertEqual(hand.get_count(), initial_hand_count - 1, "Hand count should decrease by 1")
        self.assertTrue(battlefield.contains(action_choice.id), "Played land should be on battlefield")
        self.assertFalse(hand.contains(action_choice.id), "Played land should not be in hand")

    def test_03_tap_land_for_mana(self):
        """Test tapping the played land for mana."""
        tm = self.game.turn_manager
        bf = self.game.get_zone("battlefield")

        # Advance to Precombat Main and play the land via loop
        tm.advance(self.game) # Draw
        tm.advance(self.game) # Main
        self.game.run_main_loop() # Plays land

        self.assertEqual(bf.get_count(), 1)
        land_obj = bf.get_objects(self.game)[0]
        self.assertIsInstance(land_obj, ConcretePermanent)

        # Manually tap the land and activate its mana ability
        self.assertEqual(self.player.mana_pool.get_amount(ManaType.WHITE), 0)
        
        # Find the tap mana ability
        tap_ability = None
        for ability in land_obj.abilities:
            if isinstance(ability, TapManaAbility) and ability.mana_type == ManaType.WHITE:
                tap_ability = ability
                break
        self.assertIsNotNone(tap_ability, "Plains should have a White TapManaAbility")

        # Check if it can be activated (which requires tapping)
        self.assertTrue(tap_ability.can_activate(self.game), "Ability should be activatable before tapping")

        # Tap the permanent first (game action)
        tapped = land_obj.tap()
        self.assertTrue(tapped, "Land should be tappable")
        self.assertTrue(land_obj.has_status(StatusType.TAPPED), "Land should have TAPPED status")

        # Now activate the ability (resolves immediately)
        print(f"Test: Activating ability {tap_ability}")
        tap_ability.activate(self.game) # This calls produce_mana

        # Check mana pool
        self.assertEqual(self.player.mana_pool.get_amount(ManaType.WHITE), 1, "Mana pool should have 1 white mana")

        # Try tapping again (should fail)
        tapped_again = land_obj.tap()
        self.assertFalse(tapped_again, "Already tapped land should not tap again")
        self.assertEqual(self.player.mana_pool.get_amount(ManaType.WHITE), 1, "Mana pool should still have 1 white mana")

        # Ability should not be activatable now
        self.assertFalse(tap_ability.can_activate(self.game), "Ability should not be activatable when tapped")

    def test_04_full_turn_end(self):
        """Test running the game loop until the end of the first turn."""
        self.assertFalse(self.game.game_over)

        # Run the main loop. It should play a land and eventually end the turn.
        self.game.run_main_loop()

        # The check_win_loss_condition in ConcreteGame is set to end after turn 1
        self.assertTrue(self.game.game_over, "Game should be over after run_main_loop completes turn 1")
        self.assertIsNotNone(self.game.game_result)
        self.assertEqual(self.game.game_result[0], GameResult.DRAW, "Game should end in a Draw for the test scenario")

if __name__ == '__main__':
    # To run tests easily: python -m unittest tests/test_solitaire_turn.py
    unittest.main() 