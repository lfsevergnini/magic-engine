# Magic Engine

This project is a Python-based engine designed to simulate the rules and gameplay of the trading card game Magic: The Gathering.

## Project Goal

The primary goal is to create a robust and extensible engine capable of correctly handling card interactions, game phases, player actions, and the layer system according to Magic's Comprehensive Rules.

Currently, the engine includes basic implementations for:
*   Game setup (players, decks, starting hands)
*   Core game zones (Library, Hand, Battlefield, Graveyard, Stack, Exile)
*   Turn management (phases and steps)
*   Priority handling (simplified for solitaire)
*   Basic game objects (representing cards and permanents)
*   An initial ability system (demonstrated with basic land mana abilities)
*   A simple card database structure

## Running Tests

Unit tests are included to verify the functionality of the core components. To run the tests:

1.  Ensure you have Python installed.
2.  Navigate to the root directory of the project.
3.  Run the following command in your terminal:

    ```bash
    python -m unittest discover tests
    ```

This command uses Python's built-in `unittest` module to discover and run all tests located in the `tests/` directory.

## Next Steps (Potential)

*   Implement ManaCost parsing and payment.
*   Develop the Stack properly for spell/ability resolution.
*   Build out the Layer system for continuous effects.
*   Add more card types (Creatures, Instants, Sorceries) and their interactions.
*   Implement combat logic.
*   Expand the Ability system to handle triggered and activated abilities (non-mana).
*   Integrate a more comprehensive card database (e.g., from Scryfall).
