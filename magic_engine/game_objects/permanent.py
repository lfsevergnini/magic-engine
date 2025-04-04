"""Interface for Permanent objects on the battlefield."""
from typing import Optional, Any, TYPE_CHECKING

from .base import GameObject # Inherit from base GameObject

if TYPE_CHECKING:
    # Define CombatState structure later if needed
    pass

class Permanent(GameObject):
    """Represents an object on the battlefield (Creature, Artifact, Enchantment, Land, Planeswalker, Battle)."""
    damage_marked: int = 0
    combat_state: Optional[Any] = None # Define CombatState structure later (e.g., is_attacking, is_blocking, blocked_by, blocking)
    # sumoning_sickness: bool - Handled by StatusType.SUMMONING_SICKNESS

    # Add methods specific to permanents if needed:
    # def tap(self) -> bool: ...
    # def untap(self) -> bool: ...
    # def can_attack(self, game: 'Game') -> bool: ...
    # def can_block(self, attacker: 'Permanent', game: 'Game') -> bool: ...
    pass 