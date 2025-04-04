"""Base interface for all in-game objects."""
from abc import ABC, abstractmethod
from typing import Dict, List, Set, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import ObjectId, Timestamp, PlayerId, CardOrTokenData, CharacteristicsDict, CountersDict, AttachmentsList, AttachedToObject
    from ..enums import StatusType, CounterType
    from ..player.player import Player
    from ..zones.base import Zone
    from ..game import Game
    from ..cards.ability_definition import AbilityDefinition

class GameObject(ABC):
    """Base class for all objects that exist within the game state."""
    id: 'ObjectId'
    card_data: Optional['CardOrTokenData'] # Original definition (None for AbilityOnStack?)
    owner: 'Player' # The player who started the game with the card
    controller: 'Player' # The player who currently controls the object
    current_zone: Optional['Zone'] # Optional: Might not be in a zone initially?
    timestamp: 'Timestamp' # For layer application order
    status: Set['StatusType'] # Tapped, Flipped, FaceDown, PhasedOut, etc.
    counters: 'CountersDict' # Type and count of counters
    attachments: 'AttachmentsList' # IDs of Auras/Equipment attached TO this object
    attached_to: 'AttachedToObject' # ID of object/player this Aura/Equipment is attached TO

    def __init__(self, game: 'Game', obj_id: 'ObjectId', card_data: Optional['CardOrTokenData'], owner: 'Player', controller: 'Player'):
        self.id = obj_id
        self.card_data = card_data
        self.owner = owner
        self.controller = controller
        self.current_zone = None # Must be set by subclass or move_to_zone
        self.timestamp = game.generate_timestamp() # Get timestamp from game
        # Initialize potentially shared state attributes - subclasses might override
        self.status: Set[StatusType] = set()
        self.counters: 'CountersDict' = {}
        self.attachments: 'AttachmentsList' = []
        self.attached_to: 'AttachedToObject' = None

    @abstractmethod
    def get_base_characteristics(self, game: 'Game') -> 'CharacteristicsDict':
        """Returns the characteristics directly from the CardData/TokenData."""
        pass

    @abstractmethod
    def get_characteristics(self, game: 'Game') -> 'CharacteristicsDict':
        """Calculates the object's current characteristics by applying continuous effects (via EffectManager)."""
        pass

    @abstractmethod
    def get_abilities(self, game: 'Game') -> List['AbilityDefinition']:
        """Gets the object's current abilities, considering gained/lost abilities from effects."""
        pass

    @abstractmethod
    def move_to_zone(self, target_zone: 'Zone', game: 'Game') -> None:
        """Handles the process of moving this object to a new zone, including triggering events."""
        pass

    @abstractmethod
    def add_counter(self, counter_type: 'CounterType', amount: int = 1) -> None:
        """Adds counters of a specific type to the object."""
        pass

    @abstractmethod
    def remove_counter(self, counter_type: 'CounterType', amount: int = 1) -> None:
        """Removes counters of a specific type from the object."""
        pass

    @abstractmethod
    def set_status(self, status: 'StatusType', value: bool) -> None:
        """Sets or unsets a specific status (e.g., tapped, phased out)."""
        pass

    @abstractmethod
    def has_status(self, status: 'StatusType') -> bool:
        """Checks if the object currently has a specific status."""
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass 