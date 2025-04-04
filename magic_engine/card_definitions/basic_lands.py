"""Card definitions for basic lands."""
from typing import List, Set, Optional

from ..types import CardId
from ..enums import Color, CardType, SubType, SuperType
from ..costs import ManaCost
from ..cards import CardData, AbilityDefinition

# Basic lands don't have mana costs or complex abilities defined in text.
# Their abilities (tapping for mana) are intrinsic based on their subtypes.
# We might need a way to represent these intrinsic abilities later,
# perhaps in the AbilityDefinition itself or handled directly by game rules.

class PlainsData(CardData):
    id: CardId = "plains_basic" # Example ID, use Scryfall or similar in practice
    name: str = "Plains"
    mana_cost: Optional[ManaCost] = None
    colors: Set[Color] = set()
    color_identity: Set[Color] = {Color.WHITE}
    color_indicator: Optional[Set[Color]] = None
    card_types: Set[CardType] = {CardType.LAND}
    subtypes: Set[SubType] = {SubType.PLAINS}
    supertypes: Set[SuperType] = {SuperType.BASIC}
    rules_text: str = "({T}: Add {W})"
    power: Optional[str] = None
    toughness: Optional[str] = None
    loyalty: Optional[str] = None
    defense: Optional[str] = None
    # Intrinsic mana ability, not usually listed explicitly here
    ability_definitions: List[AbilityDefinition] = []

    def get_mana_value(self) -> int:
        return 0

class ForestData(CardData):
    id: CardId = "forest_basic" # Example ID
    name: str = "Forest"
    mana_cost: Optional[ManaCost] = None
    colors: Set[Color] = set()
    color_identity: Set[Color] = {Color.GREEN}
    color_indicator: Optional[Set[Color]] = None
    card_types: Set[CardType] = {CardType.LAND}
    subtypes: Set[SubType] = {SubType.FOREST}
    supertypes: Set[SuperType] = {SuperType.BASIC}
    rules_text: str = "({T}: Add {G})"
    power: Optional[str] = None
    toughness: Optional[str] = None
    loyalty: Optional[str] = None
    defense: Optional[str] = None
    ability_definitions: List[AbilityDefinition] = []

    def get_mana_value(self) -> int:
        return 0 