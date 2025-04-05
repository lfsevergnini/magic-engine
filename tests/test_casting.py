"""Tests for casting spells."""
import unittest
import random

from magic_engine.game import ConcreteGame
from magic_engine.enums import PhaseType, StepType, ZoneType, ManaType, CardType
from magic_engine.types import DeckDict, PlayerId
from magic_engine.constants import STARTING_HAND_SIZE
# Import commands
from magic_engine.commands.base import ActionCommand
from magic_engine.commands.play_land import PlayLandCommand
from magic_engine.commands.tap_land import TapLandCommand
from magic_engine.commands.cast_spell import CastSpellCommand
from magic_engine.commands.pass_priority import PassPriorityCommand
# Import card data for tests
from magic_engine.card_definitions import PlainsData, ForestData, SavannahLionsData, GrizzlyBearsData

# Suppress print statements during tests (optional)
import builtins
_original_print = builtins.print
def muted_print(*args, **kwargs):
    pass
# builtins.print = muted_print

class TestCasting(unittest.TestCase):
    """Tests casting creature spells."""

    def setUp(self):
        """Set up a basic game scenario for casting tests."""
        random.seed(123) # Use a fixed seed for deck setup if needed
        # builtins.print = muted_print # Mute prints for setup

        self.game = ConcreteGame()
        self.player_id: PlayerId = 0
        self.opponent_id: PlayerId = 1

        # Create a deck with lands and creatures for testing
        # Player 0: Plains and Savannah Lions
        # Player 1: Forests and Grizzly Bears
        self.decks: DeckDict = {
            self.player_id: [PlainsData.id] * 10 + [SavannahLionsData.id] * 5 + [PlainsData.id] * (60-15),
            self.opponent_id: [ForestData.id] * 10 + [GrizzlyBearsData.id] * 5 + [ForestData.id] * (60-15),
        }
        self.game.start_game(self.decks)
        self.player = self.game.get_player(self.player_id)
        self.opponent = self.game.get_player(self.opponent_id)

        # builtins.print = _original_print # Restore print

        # --- Test Scenario Setup Helpers --- 
        # These helpers will modify the game state for specific tests

    def _set_phase_step(self, phase: PhaseType, step: StepType):
        """Force the game to a specific phase and step."""
        self.game.turn_manager.current_phase = phase
        self.game.turn_manager.current_step = step
        # Recalculate indices if needed by TurnManager implementation (simple version might not need)
        print(f"-- Test Setup: Forcing phase={phase.name}, step={step.name} --")

    def _give_player_mana(self, player: 'Player', mana_dict: dict[ManaType | str, int]):
        """Directly add mana to a player's pool for testing."""
        print(f"-- Test Setup: Giving mana {mana_dict} to Player {player.id} --")
        player.mana_pool._pool.clear() # Clear existing mana first
        for mana_type, amount in mana_dict.items():
             player.mana_pool.add(mana_type, amount)

    def _put_card_in_hand(self, player: 'Player', card_id: str) -> 'GameObject':
        """Creates a card object and puts it directly into the player's hand."""
        card_data = self.game.card_database.get(card_id)
        if not card_data:
            raise ValueError(f"Card ID '{card_id}' not found in database for test setup.")
        
        obj_id = self.game.generate_object_id()
        game_obj_cls = ConcretePermanent if card_data.is_permanent() else ConcreteGameObject
        # Create object without initial zone, then move it
        game_obj = game_obj_cls(self.game, obj_id, card_data, owner=player, controller=player)
        self.game.register_object(game_obj)
        hand = player.get_hand()
        game_obj.move_to_zone(hand, self.game)
        print(f"-- Test Setup: Putting {card_data.name} into Player {player.id}'s hand --")
        return game_obj

    def _put_permanent_on_battlefield(self, player: 'Player', card_id: str) -> 'Permanent':
        """Creates a permanent and puts it directly onto the battlefield."""
        card_data = self.game.card_database.get(card_id)
        if not card_data or not card_data.is_permanent():
             raise ValueError(f"Card ID '{card_id}' is not a permanent or not found.")
        
        obj_id = self.game.generate_object_id()
        # Assume ConcretePermanent for now
        perm = ConcretePermanent(self.game, obj_id, card_data, owner=player, controller=player)
        self.game.register_object(perm)
        battlefield = self.game.get_zone(ZoneId.BATTLEFIELD)
        perm.move_to_zone(battlefield, self.game) # Use move_to_zone
        # perm.enters_battlefield(self.game) # move_to_zone should handle this if implemented
        print(f"-- Test Setup: Putting {card_data.name} onto battlefield for Player {player.id} --")
        return perm

    def tearDown(self):
        """Restore print function after each test."""
        builtins.print = _original_print

    # --- Test Cases --- 

    def test_01_cast_savannah_lions_enough_mana(self):
        """Test casting Savannah Lions when having exactly W mana."""
        self._set_phase_step(PhaseType.PRECOMBAT_MAIN, StepType.MAIN)
        self.game.priority_manager.set_priority(self.player) # Give player priority
        lions_obj = self._put_card_in_hand(self.player, SavannahLionsData.id)
        self._give_player_mana(self.player, {ManaType.WHITE: 1})
        
        legal_actions = self.game._get_legal_actions(self.player)
        cast_command = next((cmd for cmd in legal_actions if isinstance(cmd, CastSpellCommand) and cmd.spell_to_cast == lions_obj), None)
        
        self.assertIsNotNone(cast_command, "Should be able to cast Savannah Lions")
        
        # Execute the command
        hand_count_before = self.player.get_hand().get_count()
        stack_count_before = self.game.get_stack().get_count()
        mana_before = self.player.mana_pool.get_amount(ManaType.WHITE)
        
        cast_command.execute(self.game, self.player)
        
        # Assertions after casting (before resolution)
        self.assertEqual(self.player.mana_pool.get_amount(ManaType.WHITE), mana_before - 1, "White mana should be spent")
        self.assertEqual(self.player.get_hand().get_count(), hand_count_before - 1, "Card should leave hand")
        self.assertEqual(self.game.get_stack().get_count(), stack_count_before + 1, "Spell should be on stack")
        self.assertEqual(self.game.get_stack().peek(), lions_obj.id, "Lions should be top of stack")
        self.assertEqual(lions_obj.zone, self.game.get_stack(), "Lions object zone should be stack")
        # Player should retain priority
        self.assertEqual(self.game.priority_manager.get_current_player(), self.player)

    def test_02_resolve_savannah_lions(self):
        """Test resolving Savannah Lions from the stack."""
        self._set_phase_step(PhaseType.PRECOMBAT_MAIN, StepType.MAIN)
        lions_obj = self._put_card_in_hand(self.player, SavannahLionsData.id)
        self._give_player_mana(self.player, {ManaType.WHITE: 1})
        
        # Cast the spell first
        legal_actions = self.game._get_legal_actions(self.player)
        cast_command = next(cmd for cmd in legal_actions if isinstance(cmd, CastSpellCommand)) 
        cast_command.execute(self.game, self.player)
        
        # Simulate passing priority by both players (assuming 1 player for simplicity now)
        # In a real game, opponent would get priority first.
        # Here, we just manually call resolve.
        stack_count_before = self.game.get_stack().get_count()
        bf_count_before = self.game.get_zone(ZoneId.BATTLEFIELD).get_count()
        
        self.game.resolve_top_stack_object()
        
        # Assertions after resolution
        self.assertEqual(self.game.get_stack().get_count(), stack_count_before - 1, "Stack should be empty")
        self.assertEqual(self.game.get_zone(ZoneId.BATTLEFIELD).get_count(), bf_count_before + 1, "Battlefield should have one permanent")
        battlefield_perm = self.game.get_zone(ZoneId.BATTLEFIELD).get_objects(self.game)[0]
        self.assertEqual(battlefield_perm.id, lions_obj.id, "Permanent on battlefield should be the Lions")
        self.assertEqual(battlefield_perm.zone, self.game.get_zone(ZoneId.BATTLEFIELD), "Lions object zone should be battlefield")
        # Check power/toughness (might need specific Permanent attributes later)
        self.assertEqual(battlefield_perm.get_power(self.game), 2)
        self.assertEqual(battlefield_perm.get_toughness(self.game), 1)
        # AP should have priority after resolution
        self.assertEqual(self.game.priority_manager.get_current_player(), self.player)
        
    def test_03_cast_grizzly_bears_not_enough_mana(self):
        """Test trying to cast Grizzly Bears with insufficient mana."""
        self._set_phase_step(PhaseType.PRECOMBAT_MAIN, StepType.MAIN)
        self.game.priority_manager.set_priority(self.player)
        bears_obj = self._put_card_in_hand(self.player, GrizzlyBearsData.id)
        self._give_player_mana(self.player, {ManaType.GREEN: 1}) # Need 1G, only have G
        
        legal_actions = self.game._get_legal_actions(self.player)
        cast_command = next((cmd for cmd in legal_actions if isinstance(cmd, CastSpellCommand) and cmd.spell_to_cast == bears_obj), None)
        
        self.assertIsNone(cast_command, "Should not be able to cast Grizzly Bears with only G")

    def test_04_cast_grizzly_bears_correct_mana(self):
        """Test casting Grizzly Bears with 1G mana."""
        self._set_phase_step(PhaseType.PRECOMBAT_MAIN, StepType.MAIN)
        self.game.priority_manager.set_priority(self.player)
        bears_obj = self._put_card_in_hand(self.player, GrizzlyBearsData.id)
        # Give exactly 1G (can be from one Forest and one Plains, for example)
        self._give_player_mana(self.player, {ManaType.GREEN: 1, ManaType.WHITE: 1})
        
        legal_actions = self.game._get_legal_actions(self.player)
        cast_command = next((cmd for cmd in legal_actions if isinstance(cmd, CastSpellCommand) and cmd.spell_to_cast == bears_obj), None)
        
        self.assertIsNotNone(cast_command, "Should be able to cast Grizzly Bears with WG")
        
        # Execute
        hand_count_before = self.player.get_hand().get_count()
        stack_count_before = self.game.get_stack().get_count()
        mana_g_before = self.player.mana_pool.get_amount(ManaType.GREEN)
        mana_w_before = self.player.mana_pool.get_amount(ManaType.WHITE)
        
        cast_command.execute(self.game, self.player)
        
        # Assertions
        self.assertEqual(self.player.mana_pool.get_amount(ManaType.GREEN), mana_g_before - 1, "Green mana should be spent")
        self.assertEqual(self.player.mana_pool.get_amount(ManaType.WHITE), mana_w_before - 1, "White mana should be spent for generic") # Assuming W is used for generic
        self.assertEqual(self.player.get_hand().get_count(), hand_count_before - 1)
        self.assertEqual(self.game.get_stack().get_count(), stack_count_before + 1)
        self.assertEqual(self.game.get_stack().peek(), bears_obj.id)

    # TODO: Add test for casting at wrong time (e.g., opponent's turn, non-main phase)
    # TODO: Add test resolving Grizzly Bears


if __name__ == '__main__':
    unittest.main() 