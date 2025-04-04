"""Concrete implementations for GameObject and its derivatives."""
from typing import Dict, List, Set, Optional, Any, TYPE_CHECKING
import copy

from .base import GameObject
from .permanent import Permanent
from ..enums import StatusType, CounterType, ManaType, SubType

if TYPE_CHECKING:
    from ..types import ObjectId, Timestamp, PlayerId, CardOrTokenData, CharacteristicsDict, CountersDict, AttachmentsList, AttachedToObject
    from ..player.player import Player
    from ..zones.base import Zone
    from ..game import Game
    from ..cards.ability_definition import AbilityDefinition
    from ..cards.card_data import CardData

class ConcreteGameObject(GameObject):
    """A concrete implementation of the base GameObject."""

    def __init__(self, game: 'Game', object_id: 'ObjectId', card_data: 'CardOrTokenData', owner: 'Player', controller: 'Player', zone: 'Zone'):
        self.game = game
        self.id: 'ObjectId' = object_id
        self.card_data: 'CardOrTokenData' = card_data
        self.owner: 'Player' = owner
        self.controller: 'Player' = controller
        self.current_zone: 'Zone' = zone
        self.timestamp: 'Timestamp' = game.generate_timestamp() # Game needs a timestamp generator
        self.status: Set['StatusType'] = set()
        self.counters: 'CountersDict' = {}
        self.attachments: 'AttachmentsList' = []
        self.attached_to: 'AttachedToObject' = None

        # Store overridden characteristics (e.g., from text-changing effects)
        # This is a simplification; a real implementation uses the layer system.
        self._overridden_characteristics: Dict[str, Any] = {}

    def get_base_characteristics(self) -> 'CharacteristicsDict':
        """Returns characteristics based on the card data."""
        if not self.card_data:
            return {}
        # This needs expansion to cover all characteristics from CardData
        base = {
            "name": self.card_data.name,
            "mana_cost": self.card_data.mana_cost,
            "colors": copy.deepcopy(self.card_data.colors),
            "card_types": copy.deepcopy(self.card_data.card_types),
            "subtypes": copy.deepcopy(self.card_data.subtypes),
            "supertypes": copy.deepcopy(self.card_data.supertypes),
            "power": self.card_data.power,
            "toughness": self.card_data.toughness,
            "loyalty": self.card_data.loyalty,
            "defense": self.card_data.defense,
        }
        return base

    def get_characteristics(self, game: 'Game') -> 'CharacteristicsDict':
        """Calculates current characteristics. For now, just returns base + overrides."""
        # TODO: Integrate with EffectManager and layer system
        base = self.get_base_characteristics()
        # Apply simple overrides (replace with layer system later)
        base.update(self._overridden_characteristics)
        # Calculate P/T based on effects/counters (simplified)
        if base.get("power") is not None:
            base["power_int"] = self._calculate_power(base, game)
        if base.get("toughness") is not None:
            base["toughness_int"] = self._calculate_toughness(base, game)

        return base

    def _calculate_power(self, base_chars: Dict, game:'Game') -> Optional[int]:
        # Simplified: just handles base P and +1/+1 counters
        # TODO: Integrate fully with layer 7
        try:
            power = int(base_chars["power"]) # Ignores '*' for now
        except (ValueError, TypeError):
            power = 0 # Or handle '*' based on CDAs

        power += self.counters.get(CounterType.PLUS_1_PLUS_1, 0)
        power -= self.counters.get(CounterType.MINUS_1_MINUS_1, 0)
        return power

    def _calculate_toughness(self, base_chars: Dict, game:'Game') -> Optional[int]:
        # Simplified: just handles base T and +1/+1 counters
        # TODO: Integrate fully with layer 7
        try:
            toughness = int(base_chars["toughness"]) # Ignores '*' for now
        except (ValueError, TypeError):
            toughness = 0 # Or handle '*' based on CDAs

        toughness += self.counters.get(CounterType.PLUS_1_PLUS_1, 0)
        toughness -= self.counters.get(CounterType.MINUS_1_MINUS_1, 0)
        return toughness

    def get_abilities(self, game: 'Game') -> List['AbilityDefinition']:
        """Gets current abilities. For now, just returns base."""
        # TODO: Integrate with EffectManager layer 6
        return self.card_data.ability_definitions if self.card_data else []

    def move_to_zone(self, target_zone: 'Zone', game: 'Game') -> None:
        """Moves the object between zones."""
        source_zone = self.current_zone
        # TODO: Publish 'ZoneChangeEvent' before and after
        if source_zone:
            source_zone.remove(self.id)
        target_zone.add(self.id)
        self.current_zone = target_zone
        # TODO: Handle status changes (e.g., losing summoning sickness on battlefield entry)
        # TODO: Handle counters/attachments falling off
        print(f"Moved {self.id} ({self.card_data.name}) from {source_zone.id} to {target_zone.id}")

    def add_counter(self, counter_type: 'CounterType', amount: int = 1) -> None:
        self.counters[counter_type] = self.counters.get(counter_type, 0) + amount
        # TODO: Publish event

    def remove_counter(self, counter_type: 'CounterType', amount: int = 1) -> None:
        current_amount = self.counters.get(counter_type, 0)
        self.counters[counter_type] = max(0, current_amount - amount)
        if self.counters[counter_type] == 0:
            del self.counters[counter_type]
        # TODO: Publish event

    def set_status(self, status: 'StatusType', value: bool) -> None:
        if value:
            self.status.add(status)
        else:
            self.status.discard(status)
        # TODO: Publish event

    def has_status(self, status: 'StatusType') -> bool:
        return status in self.status

    def __repr__(self) -> str:
        name = self.card_data.name if self.card_data else "Unknown"
        return f"Obj<{self.id}:{name}>"

class ConcretePermanent(ConcreteGameObject, Permanent):
    """Concrete implementation for permanents on the battlefield."""
    def __init__(self, game: 'Game', object_id: 'ObjectId', card_data: 'CardOrTokenData', owner: 'Player', controller: 'Player', zone: 'Zone'):
        # Initialize Permanent specific fields BEFORE calling super().__init__
        # because super init might call methods that rely on these fields.
        self.damage_marked: int = 0
        self.combat_state: Optional[Any] = None # Define CombatState later

        super().__init__(game, object_id, card_data, owner, controller, zone)

        # Apply initial statuses (e.g., summoning sickness for creatures)
        # This is simplified; rules are more complex (noncreatures becoming creatures)
        characteristics = self.get_characteristics(game)
        if CardType.CREATURE in characteristics.get("card_types", set()):
            self.set_status(StatusType.SUMMONING_SICKNESS, True)

    # --- Permanent specific methods ---
    def tap(self) -> bool:
        """Taps the permanent if able. Adds mana for basic lands (simplification)."""
        if not self.has_status(StatusType.TAPPED):
            self.set_status(StatusType.TAPPED, True)
            print(f"Tapped {self}")

            # --- Intrinsic Mana Ability Logic (Simplified) ---
            characteristics = self.get_characteristics(self.game)
            subtypes = characteristics.get("subtypes", set())
            if SubType.PLAINS in subtypes:
                self.controller.mana_pool.add(ManaType.WHITE, 1, source_id=self.id)
            elif SubType.FOREST in subtypes:
                self.controller.mana_pool.add(ManaType.GREEN, 1, source_id=self.id)
            # Add other basic land types (Island, Swamp, Mountain) here if needed
            # -----------------------------------------------

            # TODO: Publish TappedEvent
            return True
        return False

    def untap(self) -> bool:
        """Untaps the permanent."""
        if self.has_status(StatusType.TAPPED):
            self.set_status(StatusType.TAPPED, False)
            print(f"Untapped {self}")
            # TODO: Publish UntappedEvent
            return True
        return False

    def __repr__(self) -> str:
        name = self.card_data.name if self.card_data else "Unknown"
        status_str = f" ({', '.join(s.name for s in self.status)})" if self.status else ""
        return f"Perm<{self.id}:{name}{status_str}>" 