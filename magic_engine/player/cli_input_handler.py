"""Command Line Interface (CLI) input handler for player decisions."""
from typing import List, Any, TYPE_CHECKING, Dict, Optional, Callable

from .input_handler import PlayerInputHandler
from ..commands.base import ActionCommand

if TYPE_CHECKING:
    # Use forward references (strings) or TYPE_CHECKING block
    from ..types import Targetable, ModeSelection, ChoiceOptions, ChoiceResult, ObjectId
    from ..game_objects.base import GameObject
    from ..player.player import Player
    from ..game import Game
    from ..game_objects.permanent import Permanent
    from ..commands.base import ActionCommand
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

    def _choose_item_from_list(self, items: List[Any], item_type_name: str, prompt: str, display_func: Optional[Callable[[Any], str]] = None) -> Optional[Any]:
        """Generic helper to choose an item from a numbered list via CLI."""
        if not items:
            print(f"No {item_type_name} available to choose.")
            return None

        print(prompt)
        if display_func:
            options = [display_func(item) for item in items]
        else:
            options = [str(item) for item in items]
            
        while True:
            choice_str = self._display_prompt("Choose number:", options)
            try:
                choice_idx = int(choice_str) - 1
                if 0 <= choice_idx < len(items):
                    return items[choice_idx]
                else:
                    print(f"Invalid number. Please choose between 1 and {len(items)}.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def choose_card_from_list(self, cards: List['GameObject'], prompt: str) -> Optional['GameObject']:
        """Asks the player to choose a card object from a list."""
        def display_card(card):
            return card.card_data.name if card and card.card_data else "Unknown Card"
        return self._choose_item_from_list(cards, "cards", prompt, display_func=display_card)

    def choose_permanent_from_list(self, permanents: List['Permanent'], prompt: str) -> Optional['Permanent']:
        """Asks the player to choose a permanent object from a list."""
        def display_perm(perm):
             name = perm.card_data.name if perm and perm.card_data else "Unknown Permanent"
             status = "Tapped" if perm.is_tapped() else "Untapped"
             return f"{name} ({status})"
        return self._choose_item_from_list(permanents, "permanents", prompt, display_func=display_perm)

    def choose_action_with_priority(self, legal_actions: List[ActionCommand], game_state_summary: str) -> Optional[ActionCommand]:
        """Asks the player to choose an action (command object) when they have priority."""
        prompt = f"You have priority. Current State:\n{game_state_summary}\nAvailable Actions:"
        
        # Extract display names for the prompt
        action_display_names = [cmd.get_display_name() for cmd in legal_actions]

        while True:
            choice_str = self._display_prompt(prompt, action_display_names)
            if not choice_str: # Handle empty input or potential EOF cases
                print("No input received. Please choose an action.")
                continue # Or return None / default pass command?

            try:
                # Try interpreting as a number (1-based index)
                choice_idx = int(choice_str) - 1
                if 0 <= choice_idx < len(legal_actions):
                    return legal_actions[choice_idx]
                else:
                    print("Invalid number. Please choose from the list.")
            except ValueError:
                # Try interpreting as the action display name itself (case-insensitive)
                choice_lower = choice_str.lower()
                matching_actions = [
                    cmd for cmd in legal_actions
                    if cmd.get_display_name().lower() == choice_lower
                ]
                if len(matching_actions) == 1:
                    return matching_actions[0]
                elif len(matching_actions) > 1:
                     # This could happen if multiple commands have the same display name
                     # (e.g., "Activate Ability" if we don't specify which one)
                     # We might need a more robust selection mechanism later.
                     print(f"Ambiguous input '{choice_str}'. Please use the number.")
                else:
                     print(f"Invalid action '{choice_str}'. Please choose from the list or enter the corresponding number.")

            # Add a way to explicitly quit or indicate no choice
            if choice_str.lower() in ['quit', 'exit']: # Example quit command
                 print("Exiting game.")
                 # Perhaps return a special value or raise an exception
                 return None # Indicates user wants to quit or made no choice

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