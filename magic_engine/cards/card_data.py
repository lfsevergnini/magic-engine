"""Interface for the immutable definition of a card."""
from abc import ABC, abstractmethod
from typing import List, Set, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import CardId
    from ..enums import Color, CardType, SubType, SuperType
    from ..costs.mana_cost import ManaCost
    from .ability_definition import AbilityDefinition

class CardData(ABC):
    """Immutable representation of printed card data."""
    id: 'CardId'
    name: str
    mana_cost: Optional['ManaCost']
    colors: Set['Color']
    color_identity: Set['Color']
    color_indicator: Optional[Set['Color']]
    card_types: Set['CardType']
    subtypes: Set['SubType']
    supertypes: Set['SuperType']
    rules_text: str
    power: Optional[str] # String to handle '*' etc.
    toughness: Optional[str]
    loyalty: Optional[str] # For Planeswalkers
    defense: Optional[str] # For Battles
    ability_definitions: List['AbilityDefinition']

    @abstractmethod
    def get_mana_value(self) -> int:
        """Calculates the mana value based on the mana_cost."""
        pass

    # Potentially add helper methods like is_creature(), is_land(), has_subtype(), etc.
    # def is_creature(self) -> bool:
    #     return CardType.CREATURE in self.card_types 