"""Interface for the immutable definition of a card."""
from abc import ABC, abstractmethod
from typing import List, Set, Optional, TYPE_CHECKING, Type
from dataclasses import dataclass, field
from ..enums import CardType, Color, Rarity, SuperType, SubType
from ..costs.mana_cost import ManaCost

if TYPE_CHECKING:
    from ..types import CardId
    from ..enums import Color, CardType, SubType, SuperType
    from ..costs.mana_cost import ManaCost
    from .ability_definition import AbilityDefinition
    from ..game_objects.base import GameObject
    from ..abilities.base import Ability
    from ..costs.base import Cost

@dataclass(frozen=True)
class CardData:
    """Immutable definition of a card."""
    id: str # Unique card identifier (e.g., 'plains_basic')
    name: str
    card_types: Set[CardType]
    colors: Set[Color] # Usually derived from mana cost, can be set explicitly
    mana_cost: Optional[ManaCost] = None
    supertypes: Set[SuperType] = field(default_factory=set)
    subtypes: Set[SubType] = field(default_factory=set)
    rarity: Rarity = Rarity.COMMON
    text: str = ""
    flavor_text: Optional[str] = None
    power: Optional[int] = None # For creatures
    toughness: Optional[int] = None # For creatures
    loyalty: Optional[int] = None # For planeswalkers
    abilities: List[Type['Ability']] = field(default_factory=list)

    # TODO: Add fields for targeting info, alternative costs, etc.

    def __post_init__(self):
        # Basic validation
        if CardType.CREATURE in self.card_types:
            if self.power is None or self.toughness is None:
                raise ValueError(f"Creature card {self.name} must have power and toughness.")
        if CardType.PLANESWALKER in self.card_types:
            if self.loyalty is None:
                raise ValueError(f"Planeswalker card {self.name} must have loyalty.")
        # Automatically add Basic supertype if it's a basic land subtype
        basic_land_subtypes = {SubType.PLAINS, SubType.ISLAND, SubType.SWAMP, SubType.MOUNTAIN, SubType.FOREST}
        if self.subtypes.intersection(basic_land_subtypes) and not self.supertypes:
             object.__setattr__(self, 'supertypes', {SuperType.BASIC})

    def is_permanent(self) -> bool:
        """Checks if the card represents a permanent type."""
        permanent_types = {CardType.CREATURE, CardType.ARTIFACT, CardType.ENCHANTMENT, CardType.LAND, CardType.PLANESWALKER}
        return bool(self.card_types.intersection(permanent_types))

    def get_mana_value(self) -> int:
        """Calculates the mana value based on the mana_cost."""
        return self.mana_cost.get_mana_value() if self.mana_cost else 0

    # Potentially add helper methods like is_creature(), is_land(), has_subtype(), etc.
    # def is_creature(self) -> bool:
    #     return CardType.CREATURE in self.card_types 