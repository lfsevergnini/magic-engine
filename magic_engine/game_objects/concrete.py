"""Concrete implementations for GameObject and its derivatives."""
from typing import Dict, List, Set, Optional, Any, TYPE_CHECKING
import copy

from .base import GameObject
from .permanent import Permanent
from ..enums import StatusType, CounterType, ManaType, SubType, CardType

if TYPE_CHECKING:
    from ..types import ObjectId, Timestamp, CardOrTokenData, CharacteristicsDict, CountersDict, AttachmentsList, AttachedToObject
    from ..player.player import Player
    from ..zones.base import Zone
    from ..game import Game
    from ..cards.ability_definition import AbilityDefinition
    from ..cards.card_data import CardData
    from ..abilities.base import Ability

class ConcreteGameObject(GameObject):
    """A concrete implementation of the base GameObject."""

    def __init__(self, game: 'Game', object_id: 'ObjectId', card_data: 'CardOrTokenData', owner: 'Player', controller: 'Player', initial_zone: Optional['Zone']):
        self.game = game
        self.id: 'ObjectId' = object_id
        self.card_data: 'CardOrTokenData' = card_data
        self.owner: 'Player' = owner
        self.controller: 'Player' = controller
        self.current_zone: Optional['Zone'] = initial_zone
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
        source_zone_id_str = source_zone.id if source_zone else "None"

        # Update current_zone *before* modifying zone contents
        self.current_zone = target_zone

        # TODO: Publish 'ZoneChangeEvent' before and after
        target_zone.add(self.id)

        # TODO: Handle status changes (e.g., losing summoning sickness on battlefield entry)
        # TODO: Handle counters/attachments falling off
        print(f"Moved {self.id} ({self.card_data.name}) from {source_zone_id_str} to {target_zone.id}")

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

class ConcretePermanent(Permanent):
    """Concrete implementation of a permanent on the battlefield."""
    def __init__(self, game: 'Game', obj_id: int, card_data: 'CardData', owner: 'Player', controller: 'Player', zone: 'Zone'):
        # Call the Permanent's __init__ which in turn calls GameObject's
        # Do NOT pass zone here; GameObject.__init__ doesn't take it.
        super().__init__(game, obj_id, card_data, owner, controller)
        # Set zone after base initialization
        self.current_zone = zone

        # Initialize ConcretePermanent specific fields
        self.statuses: Set[StatusType] = set()
        self.damage_marked: int = 0
        self.attached_to: Optional['Permanent'] = None
        self.attachments: List['Permanent'] = []
        self.counters: Dict[CounterType, int] = {}

        # Instantiate abilities from CardData
        self.abilities: List['Ability'] = []
        if card_data.abilities:
            for ability_type in card_data.abilities:
                self.abilities.append(ability_type(source=self, controller=self.controller))

    # --- Implementation of Abstract Methods ---
    def move_to_zone(self, target_zone: 'Zone', game: 'Game') -> None:
        # Reuse the logic from ConcreteGameObject initially
        source_zone = self.current_zone
        source_zone_id_str = source_zone.id if source_zone else "None"
        self.current_zone = target_zone # Update object's current zone
        target_zone.add(self.id)       # Add object ID to target zone's list
        print(f"Moved {self.id} ({self.card_data.name}) from {source_zone_id_str} to {target_zone.id}")
        # TODO: Add event publishing (LeftZoneEvent, EnteredZoneEvent)
        # TODO: Handle zone change triggers (e.g., enters/leaves battlefield)
        # TODO: If moving from battlefield, remove from combat, remove counters/attachments?

    def get_base_characteristics(self, game: 'Game') -> Dict[str, Any]:
        # Start with printed characteristics from CardData
        # TODO: Convert CardData fields to a mutable dict? How to handle optional fields?
        # Placeholder implementation
        return {
            "name": self.card_data.name,
            "mana_cost": self.card_data.mana_cost,
            "colors": set(self.card_data.colors),
            "card_types": set(self.card_data.card_types),
            "subtypes": set(self.card_data.subtypes),
            "supertypes": set(self.card_data.supertypes),
            "abilities": list(self.card_data.abilities),
            "power": self.card_data.power,
            "toughness": self.card_data.toughness,
            "loyalty": self.card_data.loyalty,
            # ... add other relevant base characteristics
        }

    def get_characteristics(self, game: 'Game') -> Dict[str, Any]:
        # Applies continuous effects based on layers
        # For now, just return base characteristics (placeholder)
        # TODO: Implement Layer System
        base_chars = self.get_base_characteristics(game)
        # Modify base_chars based on effects (copy, control, text, type, color, ability, p/t)
        return base_chars

    def get_abilities(self, game: 'Game') -> List['Ability']:
        # Combines inherent abilities with granted abilities
        # For now, just return inherent abilities (placeholder)
        # TODO: Implement Layer 6 (Ability adding/removing effects)
        return list(self.abilities) # Return a copy

    def add_counter(self, counter_type: 'CounterType', amount: int = 1) -> None:
        """Adds counters of a specific type."""
        self.counters[counter_type] = self.counters.get(counter_type, 0) + amount
        print(f"Added {amount} {counter_type.name} counter(s) to {self}. Total: {self.counters[counter_type]}")
        # TODO: Publish CounterAddedEvent

    def remove_counter(self, counter_type: 'CounterType', amount: int = 1) -> None:
        """Removes counters of a specific type, minimum zero."""
        current_amount = self.counters.get(counter_type, 0)
        amount_to_remove = min(amount, current_amount)
        if amount_to_remove > 0:
            self.counters[counter_type] = current_amount - amount_to_remove
            print(f"Removed {amount_to_remove} {counter_type.name} counter(s) from {self}. Remaining: {self.counters[counter_type]}")
            # TODO: Publish CounterRemovedEvent
            if self.counters[counter_type] == 0:
                del self.counters[counter_type]

    # --- Statuses ---
    def set_status(self, status: StatusType, value: bool) -> None:
        if value:
            self.statuses.add(status)
        else:
            self.statuses.discard(status)

    def has_status(self, status: StatusType) -> bool:
        return status in self.statuses

    def is_tapped(self) -> bool:
        return self.has_status(StatusType.TAPPED)

    def untap(self) -> bool:
        """Untaps the permanent if able."""
        if self.has_status(StatusType.TAPPED):
            self.set_status(StatusType.TAPPED, False)
            print(f"Untapped {self}")
            # TODO: Publish UntappedEvent
            return True
        return False

    def tap(self) -> bool:
        """Taps the permanent if able."""
        if not self.has_status(StatusType.TAPPED):
            self.set_status(StatusType.TAPPED, True)
            print(f"Tapped {self}")
            # --- Removed intrinsic mana ability logic --- 
            # TODO: Publish TappedEvent or handle via TapCost/Ability Activation
            return True
        return False

    # --- Combat ---
    # ... (add combat related methods: assign_damage, deal_damage, etc.)

    # --- Counters ---
    # ... (add counter methods)

    # --- Attachments ---
    # ... (add attachment methods)

    def __repr__(self) -> str:
        status_str = f" ({', '.join(s.name for s in self.statuses)})" if self.statuses else ""
        return f"Perm<{self.id}:{self.card_data.name}{status_str}>"