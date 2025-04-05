"""Concrete implementation of the TurnManager."""
from typing import TYPE_CHECKING, List

from .turn_manager import TurnManager
from ..enums import PhaseType, StepType

if TYPE_CHECKING:
    from ..player.player import Player
    from ..game import Game
    from ..game_objects.concrete import ConcretePermanent # For untap

# Define the order of phases and steps
PHASE_ORDER = [
    PhaseType.BEGINNING,
    PhaseType.PRECOMBAT_MAIN,
    PhaseType.COMBAT,
    PhaseType.POSTCOMBAT_MAIN,
    PhaseType.ENDING,
]

STEP_ORDER = {
    PhaseType.BEGINNING: [StepType.UNTAP, StepType.UPKEEP, StepType.DRAW],
    PhaseType.PRECOMBAT_MAIN: [StepType.MAIN],
    PhaseType.COMBAT: [
        StepType.BEGIN_COMBAT,
        StepType.DECLARE_ATTACKERS,
        StepType.DECLARE_BLOCKERS,
        StepType.COMBAT_DAMAGE,
        StepType.END_OF_COMBAT,
    ],
    PhaseType.POSTCOMBAT_MAIN: [StepType.MAIN],
    PhaseType.ENDING: [StepType.END, StepType.CLEANUP],
}

class SimpleTurnManager(TurnManager):
    """A basic implementation for turn progression."""
    def __init__(self, players: List['Player'], starting_player_index: int = 0):
        if not players:
            raise ValueError("SimpleTurnManager requires at least one player.")
        self.players = players
        self.active_player_index = starting_player_index
        self.active_player: 'Player' = self.players[self.active_player_index]
        self.turn_number: int = 0
        # Initialize to before the first turn
        self.current_phase: PhaseType = PhaseType.BEGINNING
        self.current_step: StepType = StepType.UNTAP # Start at untap
        self._phase_index = 0
        self._step_index = -1 # Will be incremented to 0 on first advance

    def start_turn(self, game: 'Game') -> None:
        """Actions at the start of a new turn, including switching active player."""
        # Determine next player *before* incrementing turn number if turn > 0
        if self.turn_number > 0:
            self.active_player_index = (self.active_player_index + 1) % len(self.players)
            self.active_player = self.players[self.active_player_index]
            
        self.turn_number += 1
        print(f"\n===== Starting Turn {self.turn_number} for Player {self.active_player.id} ====")
        # Active player state reset is now handled in _perform_untap_step

        # Set phase/step indices for the beginning phase
        self._phase_index = PHASE_ORDER.index(PhaseType.BEGINNING)
        self._step_index = -1 # Will advance to Untap next
        # Active player gets priority at Upkeep (handled by advance)

    def advance(self, game: 'Game') -> None:
        """Moves to the next step or phase."""
        current_phase_steps = STEP_ORDER[self.current_phase]
        self._step_index += 1

        if self._step_index >= len(current_phase_steps):
            # Move to the next phase
            self._phase_index = (self._phase_index + 1) % len(PHASE_ORDER)
            self.current_phase = PHASE_ORDER[self._phase_index]
            self._step_index = 0
            current_phase_steps = STEP_ORDER[self.current_phase]
            # Check if it's a new turn
            if self.current_phase == PhaseType.BEGINNING:
                 # Logic suggests this should happen after cleanup before untap
                 # For simplicity here, we handle it when wrapping around
                 self.start_turn(game)
                 # Start turn resets phase/step, so we directly set the next step
                 self.current_step = STEP_ORDER[self.current_phase][self._step_index]
            else:
                self.current_step = current_phase_steps[self._step_index]
        else:
            # Move to the next step in the current phase
            self.current_step = current_phase_steps[self._step_index]

        print(f"-- Advancing to: {self.current_phase.name} Phase - {self.current_step.name} Step --")

        # --- Perform Turn-Based Actions --- (Simplified)
        if self.current_step == StepType.UNTAP:
            self._perform_untap_step(game)
        elif self.current_step == StepType.DRAW:
            self._perform_draw_step(game)
        elif self.current_step == StepType.CLEANUP:
             self._perform_cleanup_step(game)

        # --- Priority --- (Simplified)
        # Active player gets priority at the beginning of most steps/phases
        # Exception: Untap, Cleanup (usually no priority)
        if self.current_step not in [StepType.UNTAP, StepType.CLEANUP]:
            print(f"Giving priority to active player {self.active_player.id}")
            game.priority_manager.set_priority(self.active_player)
        else:
             # Clear priority during untap/cleanup unless triggers happen
             game.priority_manager.set_priority(None) # No player has priority

    def _perform_untap_step(self, game: 'Game'):
        print(f"Performing Untap Step for Player {self.active_player.id}")
        
        # Reset turn-based state for active player (e.g., land drops)
        self.active_player.reset_turn_based_state()
        
        battlefield = game.get_zone("battlefield")
        permanents = battlefield.get_objects(game)
        for perm in permanents:
            # Check controller matches active player
            if isinstance(perm, ConcretePermanent) and perm.controller == self.active_player:
                 perm.untap() # ConcretePermanent handles check if already untapped
            # TODO: Handle phasing

    def _perform_draw_step(self, game: 'Game'):
        print(f"Performing Draw Step for Player {self.active_player.id}")
        # First draw in a turn is a turn-based action
        if self.turn_number > 0: # Don't draw on the conceptual turn 0 start
             self.active_player.draw_cards(1)

    def _perform_cleanup_step(self, game: 'Game'):
        print(f"Performing Cleanup Step for Player {self.active_player.id}")
        # Discard down to max hand size (TODO)
        # Remove "until end of turn" effects (TODO)
        # Remove damage from creatures (TODO)
        # Empty mana pools
        for player in game.players:
            player.mana_pool.empty()
        # Check SBAs and Triggers. If any happen, players get priority and another cleanup step occurs. (TODO)

    def current_turn_player(self) -> 'Player':
        return self.active_player

    # Re-add set_active_player to satisfy the abstract base class
    def set_active_player(self, player: 'Player') -> None:
        """Sets the active player. Used for game start or effects that change active player.
        Updates the internal index if the player is in the manager's list."""
        self.active_player = player
        # Update the index if the new player is in our list
        try:
            self.active_player_index = self.players.index(player)
        except ValueError:
            # Player is not in the list managed by this turn manager
            # This might happen with control-changing effects temporarily
            print(f"Warning: Set active player {player.id} who is not in the turn manager's player list.")
            # Keep the index as is, or set to -1? Let's keep it for now.
            pass

    # def set_active_player(self, player: 'Player') -> None:
    #     # Used for game start or effects that change active player
    #     self.active_player = player 