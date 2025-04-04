"""Interface for managing the combat phase."""
from abc import ABC, abstractmethod
from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import ObjectId, PlayerId, PlayerChoices, BlockerDeclarationChoices, BlockerOrderChoices, DamageAssignment
    from ..game import Game
    from ..game_objects.permanent import Permanent
    from ..player.player import Player

class CombatManager(ABC):
    """Manages combat state and actions within the combat phase."""
    attackers: Dict['ObjectId', 'PlayerId' | 'ObjectId'] # Attacker ID -> Target ID (Player or Planeswalker)
    blockers: Dict['ObjectId', List['ObjectId']] # Blocker ID -> List of Attacker IDs it's blocking
    blocker_order: Dict['ObjectId', List['ObjectId']] # Attacker ID -> Ordered list of Blockers blocking it
    # ... other combat state info (e.g., creatures removed from combat)

    @abstractmethod
    def declare_attackers(self, choices: 'PlayerChoices', game: 'Game') -> None:
        """Processes the active player's declaration of attackers."""
        pass

    @abstractmethod
    def declare_blockers(self, choices: 'BlockerDeclarationChoices', game: 'Game') -> None:
        """Processes the defending player's declaration of blockers."""
        pass

    @abstractmethod
    def order_blockers(self, choices: 'BlockerOrderChoices', game: 'Game') -> None:
        """Processes the active player's ordering of blockers for each attacker."""
        pass

    @abstractmethod
    def assign_combat_damage(self, assignments: 'DamageAssignment', game: 'Game') -> None:
        """Processes the players' assignment of combat damage (for creatures with >1 power/toughness or multiple blockers/attackers)."""
        pass

    @abstractmethod
    def deal_combat_damage(self, game: 'Game') -> None:
        """Deals the assigned or calculated combat damage simultaneously."""
        pass

    @abstractmethod
    def clear_combat(self) -> None:
        """Resets combat state at the end of the combat phase."""
        pass

    @abstractmethod
    def get_legal_attackers(self, player: 'Player', game: 'Game') -> List['Permanent']:
        """Returns the list of creatures controlled by the player that can legally attack."""
        pass

    @abstractmethod
    def get_legal_blockers(self, attacker: 'Permanent', defending_player: 'Player', game: 'Game') -> List['Permanent']:
        """Returns the list of creatures controlled by the defending player that can legally block the specified attacker."""
        pass 