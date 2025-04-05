from typing import List, Tuple
from ..cards.card_data import CardData
from ..enums import CardType, ManaType, Subtype
from ..costs.mana_cost import ManaCost

class SavannahLionsData(CardData):
    id: str = "savannah_lions_u0146"
    name: str = "Savannah Lions"
    mana_cost: ManaCost = ManaCost(generic=0, white=1)
    card_types: Tuple[CardType, ...] = (CardType.CREATURE,)
    subtypes: Tuple[Subtype, ...] = (Subtype.CAT,)
    power: int = 2
    toughness: int = 1
    # No abilities for vanilla creature 