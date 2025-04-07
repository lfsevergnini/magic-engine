from typing import List, Tuple

from ..cards.ability_definition import AbilityDefinition
from ..cards.card_data import CardData
from ..enums import CardType, ManaType, SubType
from ..costs.mana_cost import SimpleManaCost

class SavannahLionsData(CardData):
    id: str = "savannah_lions_u0146"
    name: str = "Savannah Lions"
    mana_cost: SimpleManaCost = SimpleManaCost(white=1)
    card_types: Tuple[CardType, ...] = (CardType.CREATURE,)
    subtypes: Tuple[SubType, ...] = (SubType.CAT,)
    power: int = 2
    toughness: int = 1
    abilities: List[AbilityDefinition] = []
