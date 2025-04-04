"""Card definitions for basic lands."""
from typing import List, Set, Optional

from ..types import CardId
from ..enums import Color, CardType, SubType, SuperType, Rarity, ManaType
from ..costs import ManaCost
from ..cards import CardData, AbilityDefinition
from ..abilities.mana_ability import TapManaAbility

# Basic lands don't have mana costs or complex abilities defined in text.
# Their abilities (tapping for mana) are intrinsic based on their subtypes.
# We might need a way to represent these intrinsic abilities later,
# perhaps in the AbilityDefinition itself or handled directly by game rules.

PlainsData = CardData(
    id="plains_basic",
    name="Plains",
    card_types={CardType.LAND},
    supertypes={SuperType.BASIC},
    subtypes={SubType.PLAINS},
    colors=set(), # Lands are colorless
    abilities=[lambda source, controller: TapManaAbility(source, controller, ManaType.WHITE)],
    text="({T}: Add {W}.)" # Reminder text
)

ForestData = CardData(
    id="forest_basic",
    name="Forest",
    card_types={CardType.LAND},
    supertypes={SuperType.BASIC},
    subtypes={SubType.FOREST},
    colors=set(),
    abilities=[lambda source, controller: TapManaAbility(source, controller, ManaType.GREEN)],
    text="({T}: Add {G}.)"
)

# TODO: Island, Swamp, Mountain

# --- REMOVE OLD CLASSES --- #
# class PlainsData(CardData):
#     id = "plains_basic"
#     name = "Plains"
#     mana_cost = None
#     colors = set()
#     color_identity = {Color.WHITE}
#     color_indicator = None
#     card_types = {CardType.LAND}
#     subtypes = {SubType.PLAINS}
#     supertypes = {SuperType.BASIC}
#     rules_text = ""
#     power = None
#     toughness = None
#     loyalty = None
#     defense = None
#     ability_definitions = []
#
#     def get_mana_value(self) -> int:
#         return 0
#
# class ForestData(CardData):
#     id = "forest_basic"
#     name = "Forest"
#     mana_cost = None
#     colors = set()
#     color_identity = {Color.GREEN}
#     color_indicator = None
#     card_types = {CardType.LAND}
#     subtypes = {SubType.FOREST}
#     supertypes = {SuperType.BASIC}
#     rules_text = ""
#     power = None
#     toughness = None
#     loyalty = None
#     defense = None
#     ability_definitions = []
#
#     def get_mana_value(self) -> int:
#         return 0 