"""Type Aliases for Clarity"""
from typing import TYPE_CHECKING, TypeAlias, Union, Any, Dict, List, Set, Optional

# Forward declarations might be needed here depending on final structure
# to avoid circular imports while still enabling type checking.

PlayerId: TypeAlias = int
ObjectId: TypeAlias = int # Unique ID for in-game objects
CardId: TypeAlias = str   # Scryfall ID or similar
ZoneId: TypeAlias = str   # e.g., "library_player1", "battlefield"
Timestamp: TypeAlias = int # For layer system

# Forward declare classes used in complex type hints
# This allows type checkers to understand the structure without runtime imports.
# We'll use typing.TYPE_CHECKING in actual class files for conditional imports.
if TYPE_CHECKING: # - Pylance/MyPy understand this idiom
    # Define placeholder classes or import them here
    from .enums import Color, CardType, SubType, SuperType, ManaType, ManaSymbol, PhaseType, StepType, LayerType, CounterType, StatusType, VisibilityType, ZoneType, GameResult
    from .game import Game
    from .player.player import Player
    from .cards import CardData, TokenData, AbilityDefinition
    from .game_objects.base import GameObject
    from .game_objects.permanent import Permanent
    from .game_objects.spell import Spell
    from .game_objects.ability_on_stack import AbilityOnStack
    from .zones import Zone, Stack
    from .effects.base import Effect
    from .effects.continuous import ContinuousEffect, ReplacementEffect, PreventionEffect
    from .managers.effect_manager import EffectManager
    from .costs import Cost, ManaCost
    from .player.mana_pool import ManaPool
    from .managers.turn_manager import TurnManager
    from .managers.priority_manager import PriorityManager
    from .managers.combat_manager import CombatManager
    from .state.state_based_actions import StateBasedActionChecker
    from .events import EventBus, Event
    from .player.input_handler import PlayerInputHandler
    # Define placeholder complex types used within aliases
    class TargetInfo: pass
    class Mode: pass
    class CastingCostInfo: pass
    class DependencyInfo: pass
    class Duration: pass
    class SacrificeRequirement: pass
    class DiscardRequirement: pass
    class ManaRestriction: pass
    class GameState: pass

# --- Type Aliases --- Needed across multiple modules
Targetable = Union['GameObject', 'Player']
CardOrTokenData = Union['CardData', 'TokenData']
CharacteristicValue = Any # Placeholder for various characteristic types
CharacteristicsDict = Dict[str, CharacteristicValue]
TargetSelection = Union['GameObject', 'Player']
ModeSelection = 'Mode'
ChoiceOptions = List[Any]
ChoiceResult = Any
PlayerChoices = Dict[ObjectId, Union[PlayerId, ObjectId]] # Attacker ID -> Target ID (Player or Planeswalker)
BlockerDeclarationChoices = Dict[ObjectId, ObjectId] # Blocker ID -> Attacker ID
BlockerOrderChoices = Dict[ObjectId, List[ObjectId]] # Blocker ID -> Ordered list of Attacker IDs it's blocking
DamageAssignment = Dict[ObjectId, Dict[ObjectId, int]] # Attacker/Blocker -> {Target -> Amount}
SpellCastingOptions = Dict[str, Any] # Targets, modes, X value, additional costs, etc.
AbilityActivationOptions = Dict[str, Any] # Targets, modes, etc.
SpecialActionOptions = Optional[Dict[str, Any]]
DeckList = List[CardId]
DeckDict = Dict[PlayerId, DeckList]
CountersDict = Dict['CounterType', int]
AttachmentsList = List[ObjectId]
AttachedToObject = Optional[Union[ObjectId, PlayerId]] 