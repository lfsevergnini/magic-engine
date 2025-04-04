"""Mana abilities."""
from typing import TYPE_CHECKING, List
from abc import abstractmethod
from .base import Ability
from ..costs.base import Cost
from ..costs.concrete import TapCost
from ..enums import ManaType

if TYPE_CHECKING:
    from ..game import Game
    from ..player.player import Player
    from ..game_objects.permanent import Permanent


class ManaAbility(Ability):
    """Base class for abilities that produce mana."""
    @abstractmethod
    def produce_mana(self, game: 'Game') -> None:
        """Adds the mana to the controller's pool."""
        pass

    def activate(self, game: 'Game') -> None:
        # Basic mana abilities don't use the stack, they just resolve.
        # Cost payment (e.g., tapping) is assumed to happen as part of the activation process
        # or was checked by can_activate. We just produce the mana.
        self.produce_mana(game)


class TapManaAbility(ManaAbility):
    """A mana ability activated by tapping the source permanent.
       Produces one mana of a specified type.
    """
    def __init__(self, source: 'Permanent', controller: 'Player', mana_type: ManaType):
        # The cost is implicitly tapping the source.
        # We represent it explicitly for potential future use (e.g., checking costs)
        # but the actual tap action is handled externally.
        super().__init__(source=source, controller=controller, cost=[TapCost(source)])
        self.mana_type = mana_type

    def can_activate(self, game: 'Game') -> bool:
        """Can activate if the source permanent is untapped."""
        # Cast source to Permanent for type checking/IDE help
        source_permanent: 'Permanent' = self.source # type: ignore
        return not source_permanent.is_tapped()

    def produce_mana(self, game: 'Game') -> None:
        """Adds one mana of the specified type to the controller's pool."""
        self.controller.mana_pool.add(self.mana_type, 1, source_id=self.source.id)
        # No print here, mana pool add handles it

    def __repr__(self) -> str:
        return f"TapAbility<{self.source.card_data.name} -> {self.mana_type.name}>" 