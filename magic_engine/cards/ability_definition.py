"""Interface for the abstract definition of a card ability."""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Define Cost properly
    from ..costs.base import Cost
    # Define EffectDescription, TriggerCondition etc. as needed

class AbilityDefinition(ABC):
    """Abstract definition of an ability (static, triggered, activated)."""
    # This needs significant design - could be function references,
    # data structures holding effect descriptions, pointers to script functions, etc.

    ability_type: str # Static, Triggered, Activated, ManaAbility, SpellAbility, etc.

    # Potential properties depending on type:
    # cost: Optional['Cost'] = None # For activated abilities
    # effect_description: Any = None # How to represent the effect?
    # trigger_condition: Any = None # How to represent the trigger?
    # target_specification: Any = None # How to specify legal targets?
    # is_mana_ability: bool = False

    # Methods might be needed to generate the actual effect or check legality 