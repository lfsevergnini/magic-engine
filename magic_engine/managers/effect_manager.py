"""Interface for the manager of continuous effects and layer application."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..game import Game
    from ..game_objects.base import GameObject
    from ..effects.continuous import ContinuousEffect, ReplacementEffect, PreventionEffect
    from ..events.base import Event
    from ..types import CharacteristicsDict

class EffectManager(ABC):
    """Manages continuous effects and applies layers to determine object characteristics."""
    @abstractmethod
    def add_effect(self, effect: 'ContinuousEffect') -> None:
        """Registers a new continuous effect."""
        pass

    @abstractmethod
    def remove_effect(self, effect: 'ContinuousEffect') -> None:
        """Removes a specific continuous effect (e.g., when its source leaves)."""
        pass

    @abstractmethod
    def remove_expired_effects(self, game: 'Game') -> None:
        """Removes effects whose duration has ended."""
        pass

    @abstractmethod
    def get_characteristics(self, obj: 'GameObject', game: 'Game') -> 'CharacteristicsDict':
        """Calculates final characteristics by applying all relevant effects in layer order, handling dependencies."""
        pass

    @abstractmethod
    def get_abilities(self, obj: 'GameObject', game: 'Game') -> List[Any]: # Define Ability more precisely
        """Calculates the final set of abilities an object has, considering effects that grant or remove abilities."""
        pass

    @abstractmethod
    def get_replacement_effects(self, event: 'Event', game: 'Game') -> List['ReplacementEffect']:
        """Finds all active replacement effects that could modify the given event."""
        pass

    @abstractmethod
    def get_prevention_effects(self, damage_event: 'Event', game: 'Game') -> List['PreventionEffect']:
        """Finds all active prevention effects that could modify the given damage event."""
        pass 