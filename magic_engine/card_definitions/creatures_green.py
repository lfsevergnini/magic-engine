from typing import List, Tuple
from ..cards.card_data import CardData
from ..enums import CardType, ManaType, Subtype
from ..costs.mana_cost import SimpleManaCost

class GrizzlyBearsData(CardData):
    id: str = "grizzly_bears_xxx" # Placeholder ID, update if known
    name: str = "Grizzly Bears"
    mana_cost: SimpleManaCost = SimpleManaCost(generic=1, green=1)
    card_types: Tuple[CardType, ...] = (CardType.CREATURE,)
    subtypes: Tuple[Subtype, ...] = (Subtype.BEAR,)
    power: int = 2
    toughness: int = 2
    # No abilities for vanilla creature 