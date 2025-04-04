"""Interface for the definition of a predefined token."""
from typing import TYPE_CHECKING

from .card_data import CardData # Inherit structure

if TYPE_CHECKING:
    # Add any specific imports for tokens if needed
    pass

# Tokens often share the same structure as CardData but aren't represented
# by physical cards in the deck and have specific rules (e.g., cease to exist
# when leaving the battlefield).
# We can inherit from CardData to reuse the structure, or define separately
# if the differences warrant it.
class TokenData(CardData):
    """Immutable representation of predefined token data.

    Inherits most fields from CardData but represents a token.
    """
    # No additional abstract methods needed if it just uses CardData's structure.
    # Implementations might override methods like get_mana_value (usually 0 for tokens).
    pass 