"""Command Line Interface (CLI) input handler for player decisions."""
from typing import List, Any, TYPE_CHECKING, Dict, Optional

from .input_handler import PlayerInputHandler

if TYPE_CHECKING:
    # Use forward references (strings) or TYPE_CHECKING block
    from ..types import Targetable, ModeSelection, ChoiceOptions, ChoiceResult, ObjectId
    from ..game_objects.base import GameObject
    from ..player.player import Player
    from ..game import Game
    # from ..cards import Mode # Define Mode properly later
    class Mode:
        pass

class CliInputHandler(PlayerInputHandler):
    """Handles player decisions via the command line."""
    def __init__(self, player: 'Player', game: 'Game'):
        self.player = player
        self.game = game

    def _display_prompt(self, prompt: str, options: Optional[List[str]] = None) -> str:
        """Helper to display prompts and get input."""
        print(f"\n--- Player {self.player.id} Turn --- ")
        print(prompt)
        if options:
            for i, option in enumerate(options):
                print(f"  {i+1}. {option}")
        while True:
            try:
                choice = input("> ").strip()
                return choice
            except EOFError: # Handle Ctrl+D or similar
                 print("\nInput closed unexpectedly. Exiting.")
                 # Potentially raise a specific exception or exit
                 raise SystemExit
            except Exception as e:
                 print(f"An error occurred: {e}")


    def choose_action_with_priority(self, legal_actions: List[str], game_state_summary: str) -> str:
        """Asks the player to choose an action when they have priority."""
        prompt = f"You have priority. Current State:\n{game_state_summary}\nAvailable Actions:"
        
        while True:
            choice_str = self._display_prompt(prompt, legal_actions)
            try:
                # Try interpreting as a number (1-based index)
                choice_idx = int(choice_str) - 1
                if 0 <= choice_idx < len(legal_actions):
                    return legal_actions[choice_idx]
                else:
                    print("Invalid number. Please choose from the list.")
            except ValueError:
                # Try interpreting as the action string itself (case-insensitive)
                choice_lower = choice_str.lower()
                matching_actions = [action for action in legal_actions if action.lower() == choice_lower]
                if len(matching_actions) == 1:
                    return matching_actions[0]
                elif len(matching_actions) > 1:
                     # This shouldn't happen with distinct actions, but handle just in case
                     print("Ambiguous input. Please be more specific or use the number.")
                else:
                     print(f"Invalid action '{choice_str}'. Please choose from the list or enter the corresponding number.")

    # --- Stub Implementations for other choices ---

    def choose_target(self, legal_targets: List['Targetable'], prompt: str) -> 'Targetable':
        print(f"[STUB] Choosing target: {prompt}")
        # TODO: Implement proper CLI selection
        if not legal_targets:
            raise ValueError("Cannot choose target from empty list.")
        print("Auto-selecting first target.")
        return legal_targets[0]

    def choose_targets(self, legal_targets: List['Targetable'], num_targets: int, min_targets: int, prompt: str) -> List['Targetable']:
        print(f"[STUB] Choosing {num_targets} targets (min {min_targets}): {prompt}")
        # TODO: Implement proper CLI selection
        if len(legal_targets) < min_targets:
             raise ValueError(f"Not enough legal targets ({len(legal_targets)}) to meet minimum ({min_targets}).")
        num_to_select = min(num_targets, len(legal_targets))
        print(f"Auto-selecting first {num_to_select} targets.")
        return legal_targets[:num_to_select]

    def choose_mode(self, legal_modes: List['Mode'], prompt: str) -> 'ModeSelection':
        print(f"[STUB] Choosing mode: {prompt}")
        # TODO: Implement proper CLI selection
        if not legal_modes:
            raise ValueError("Cannot choose mode from empty list.")
        print("Auto-selecting first mode.")
        # Assuming ModeSelection is just the chosen mode for now
        return legal_modes[0] # Placeholder

    def choose_yes_no(self, prompt: str) -> bool:
        print(f"[STUB] Choosing Yes/No: {prompt}")
        # TODO: Implement proper CLI selection
        print("Auto-selecting Yes.")
        return True

    def choose_order(self, items: List[Any], prompt: str) -> List[Any]:
        print(f"[STUB] Choosing order: {prompt}")
        # TODO: Implement proper CLI selection
        print("Keeping original order.")
        return items

    def choose_card_to_discard(self, hand: List['GameObject'], count: int, random: bool, prompt: str) -> List['GameObject']:
        print(f"[STUB] Choosing card to discard: {prompt}")
        # TODO: Implement proper CLI selection
        if len(hand) < count:
             raise ValueError(f"Not enough cards in hand ({len(hand)}) to discard {count}.")
        print(f"Auto-discarding first {count} cards.")
        return hand[:count]

    def choose_distribution(self, total: int, categories: List[Any], prompt: str) -> Dict[Any, int]:
        print(f"[STUB] Choosing distribution: {prompt}")
        # TODO: Implement proper CLI selection
        print("Distributing evenly (integer division).")
        dist = {}
        base = total // len(categories)
        rem = total % len(categories)
        for i, cat in enumerate(categories):
            dist[cat] = base + (1 if i < rem else 0)
        return dist

    def make_generic_choice(self, options: 'ChoiceOptions', prompt: str) -> 'ChoiceResult':
        print(f"[STUB] Making generic choice: {prompt}")
        # TODO: Implement proper CLI selection based on ChoiceOptions structure
        if not options: # Assuming options is list-like or dict-like
             raise ValueError("Cannot make choice from empty options.")
        print("Auto-selecting first option.")
        # Assuming ChoiceResult is the option itself
        if isinstance(options, list):
            return options[0]
        elif isinstance(options, dict):
            return next(iter(options.values())) # Or keys? Depends on ChoiceOptions/Result
        else:
             raise TypeError(f"Unsupported options type: {type(options)}") 