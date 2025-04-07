from typing import List, Tuple
from ..cards.card_data import CardData
from ..cards.ability_definition import AbilityDefinition
from ..enums import CardType, ManaType, SubType
from ..costs.mana_cost import SimpleManaCost

class GrizzlyBearsData(CardData):
    id: str = "grizzly_bears_xxx" # Placeholder ID, update if known
    name: str = "Grizzly Bears"
    mana_cost: SimpleManaCost = SimpleManaCost(generic=1, green=1)
    card_types: Tuple[CardType, ...] = (CardType.CREATURE,)
    subtypes: Tuple[SubType, ...] = (SubType.BEAR,)
    power: int = 2
    toughness: int = 2
    abilities: List[AbilityDefinition] = []
