"""Entry point for running a local two-player CLI Magic game."""

import random

# Attempt to import from the magic_engine package
try:
    from magic_engine.game import ConcreteGame
    from magic_engine.types import DeckDict, PlayerId
    from magic_engine.constants import STARTING_LIBRARY_SIZE
except ImportError:
    # Handle if run from root or tests directory
    import sys
    import os
    # Add the parent directory (containing magic_engine) to the path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from magic_engine.game import ConcreteGame
    from magic_engine.types import DeckDict, PlayerId
    from magic_engine.constants import STARTING_LIBRARY_SIZE

def create_basic_decks() -> DeckDict:
    """Creates two simple decks for testing."""
    player_0_id: PlayerId = 0
    player_1_id: PlayerId = 1

    # Assuming card IDs are simple strings like 'plains_basic' and 'forest_basic'
    # These must match the IDs loaded in ConcreteGame._load_card_database
    deck_0 = ["plains_basic"] * STARTING_LIBRARY_SIZE
    deck_1 = ["forest_basic"] * STARTING_LIBRARY_SIZE

    decks = {
        player_0_id: deck_0,
        player_1_id: deck_1
    }
    return decks

def main():
    """Sets up and runs the CLI game."""
    print("Welcome to Magic Engine CLI!")
    print("Setting up a new game...")

    # Seed random for potential future use (e.g., determining starting player)
    random.seed()

    game = ConcreteGame()
    decks = create_basic_decks()

    try:
        game.start_game(decks)
        game.run_main_loop()
    except Exception as e:
        print(f"\nFATAL ERROR: An unexpected error occurred during gameplay:")
        print(f"  {type(e).__name__}: {e}")
        # Optionally print traceback for debugging
        import traceback
        traceback.print_exc()
    finally:
        print("\nExiting Magic Engine CLI. Goodbye!")

if __name__ == "__main__":
    main()
