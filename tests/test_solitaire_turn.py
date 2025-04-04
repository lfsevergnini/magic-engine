"""Unit tests for the solitaire game scenario."""
import unittest
import sys
import os

# Adjust path to import from the parent directory (magic_engine)
# This is often needed when running tests from the tests/ directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from magic_engine.game import ConcreteGame
from magic_engine.enums import PhaseType, StepType, ZoneType, ManaType
from magic_engine.types import DeckDict, PlayerId

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
        # Suppress prints for setup
        # old_print = builtins.print
        # builtins.print = muted_print

        self.game = ConcreteGame()
        self.player_id: PlayerId = 0
        # Deck consists of 60 Plains cards
        self.deck: DeckDict = {self.player_id: ["plains_basic"] * 60}
        self.game.start_game(self.deck)
        self.player = self.game.get_player(self.player_id)

        # Restore print function if it was muted
        # builtins.print = old_print

        # Ensure setup finished correctly
        self.assertIsNotNone(self.player)
        self.assertEqual(len(self.game.players), 1)
        self.assertEqual(self.player.get_library().get_count(), 53) # 60 - 7 draw
        self.assertEqual(self.player.get_hand().get_count(), 7)
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
        self.assertEqual(self.player.get_hand().get_count(), 8)

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
        tm = self.game.turn_manager
        bf = self.game.get_zone("battlefield")
        hand = self.player.get_hand()

        # Advance to Precombat Main Phase
        tm.advance(self.game) # Draw -> Hand=8
        tm.advance(self.game) # Main Phase
        self.assertEqual(tm.current_phase, PhaseType.PRECOMBAT_MAIN)
        self.assertEqual(bf.get_count(), 0)
        self.assertEqual(self.player.lands_played_this_turn, 0)
        initial_hand_count = hand.get_count()

        # Run the loop until priority is passed (which should play the land)
        # The AutoPlayerInputHandler should detect the playable land and choose it.
        # The game loop should then call player.play_land.
        self.game.run_main_loop() # Let the loop run one priority cycle

        # Check assertions AFTER the loop step that played the land
        self.assertEqual(self.player.lands_played_this_turn, 1, "Land drop count should be 1")
        self.assertEqual(bf.get_count(), 1, "Battlefield should have 1 land")
        self.assertEqual(hand.get_count(), initial_hand_count - 1, "Hand count should decrease by 1")

        # Verify the land on battlefield is a Plains
        land_obj = bf.get_objects(self.game)[0]
        self.assertEqual(land_obj.card_data.name, "Plains")

        # Try to play another land (should fail)
        land_in_hand = None
        for card_obj in hand.get_objects(self.game):
            if ZoneType.LAND in card_obj.card_data.card_types:
                 land_in_hand = card_obj
                 break
        self.assertIsNotNone(land_in_hand, "Player should still have lands in hand")
        self.assertFalse(self.player.can_play_land(land_in_hand, hand), "Should not be able to play a second land")

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

        # Manually tap the land (tests don't usually interact with input handler directly)
        self.assertEqual(self.player.mana_pool.get_amount(ManaType.WHITE), 0)
        tapped = land_obj.tap()
        self.assertTrue(tapped, "Land should be tappable")
        self.assertTrue(land_obj.has_status(StatusType.TAPPED), "Land should have TAPPED status")

        # Check mana pool
        self.assertEqual(self.player.mana_pool.get_amount(ManaType.WHITE), 1, "Mana pool should have 1 white mana")

        # Try tapping again (should fail)
        tapped_again = land_obj.tap()
        self.assertFalse(tapped_again, "Already tapped land should not tap again")
        self.assertEqual(self.player.mana_pool.get_amount(ManaType.WHITE), 1, "Mana pool should still have 1 white mana")

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