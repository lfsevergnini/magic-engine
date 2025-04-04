"""Interface for tracking global game states."""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Imports for type checking
    pass

class GameState(ABC):
    """Tracks global game states like Monarch, Initiative, Day/Night."""
    # Properties for Monarch player, Initiative player, Day/Night status, etc.
    # Example property (needs concrete implementation later)
    # monarch_player_id: Optional[PlayerId] = None
    # initiative_player_id: Optional[PlayerId] = None
    # is_day: bool = True
    pass 