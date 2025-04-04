"""Enums representing core Magic: The Gathering concepts."""
from enum import Enum, auto

# Define these enums properly with members in your implementation

class Color(Enum):
    WHITE = auto()
    BLUE = auto()
    BLACK = auto()
    RED = auto()
    GREEN = auto()
    COLORLESS = auto() # Technically not a color, but often needed

class CardType(Enum):
    CREATURE = auto()
    LAND = auto()
    INSTANT = auto()
    SORCERY = auto()
    ARTIFACT = auto()
    ENCHANTMENT = auto()
    PLANESWALKER = auto()
    BATTLE = auto()
    TRIBAL = auto() # Special case
    # Add others as needed (e.g., Conspiracy, Scheme)

class SubType(Enum):
    # This will be a very long list! e.g., Goblin, Elf, Island, Aura, Equipment...
    # Basic Lands
    ISLAND = auto()
    FOREST = auto()
    PLAINS = auto()
    MOUNTAIN = auto()
    SWAMP = auto()
    # Creatures
    GOBLIN = auto()
    ELF = auto()
    CAT = auto()
    BEAR = auto()
    # The rest
    AURA = auto()
    EQUIPMENT = auto()
    # ... add many more

class SuperType(Enum):
    BASIC = auto()
    LEGENDARY = auto()
    SNOW = auto()
    WORLD = auto()
    ONGOING = auto() # For Schemes
    HOST = auto() # For Augment

class ManaType(Enum):
    WHITE = auto()
    BLUE = auto()
    BLACK = auto()
    RED = auto()
    GREEN = auto()
    COLORLESS = auto()

class ManaSymbol(Enum):
    # Represents symbols like {W}, {U}, {B}, {R}, {G}, {C}, {X}, {0}, {1}...,
    # {W/U}, {2/W}, {W/P}, {S} (Snow), etc.
    # Needs careful design - maybe classes instead of a simple enum?
    W = auto()
    U = auto()
    B = auto()
    R = auto()
    G = auto()
    C = auto()
    X = auto()
    GENERIC_0 = auto()
    GENERIC_1 = auto()
    GENERIC_2 = auto()
    # ... Generic numbers
    WU = auto() # Hybrid
    WP = auto() # Phyrexian
    SNOW = auto()
    # ... etc.

class PhaseType(Enum):
    BEGINNING = auto()
    PRECOMBAT_MAIN = auto()
    COMBAT = auto()
    POSTCOMBAT_MAIN = auto()
    ENDING = auto()

class StepType(Enum):
    UNTAP = auto()
    UPKEEP = auto()
    DRAW = auto()
    BEGIN_COMBAT = auto()
    DECLARE_ATTACKERS = auto()
    DECLARE_BLOCKERS = auto()
    COMBAT_DAMAGE = auto()
    END_OF_COMBAT = auto()
    MAIN = auto() # Used for Pre/Postcombat Main Phases
    END = auto()
    CLEANUP = auto()

class LayerType(Enum):
    LAYER_1_COPY = auto()
    LAYER_2_CONTROL = auto()
    LAYER_3_TEXT = auto()
    LAYER_4_TYPE = auto()
    LAYER_5_COLOR = auto()
    LAYER_6_ABILITY = auto()
    LAYER_7A_PT_SET = auto()          # P/T setting CDA
    LAYER_7B_PT_MODIFY = auto()       # P/T setting/modifying effects
    LAYER_7C_PT_COUNTERS = auto()     # P/T modification from counters
    LAYER_7D_PT_SWITCH = auto()       # P/T switching
    # Note: Some interpretations group 7a-7d, others keep separate

class CounterType(Enum):
    PLUS_1_PLUS_1 = auto()
    MINUS_1_MINUS_1 = auto()
    LOYALTY = auto()
    POISON = auto()
    CHARGE = auto()
    FATE = auto()
    FEATHER = auto()
    TIME = auto()
    # ... many others

class StatusType(Enum):
    TAPPED = auto()
    FLIPPED = auto()
    FACE_DOWN = auto()
    PHASED_OUT = auto()
    SUMMONING_SICKNESS = auto()
    MONSTROUS = auto()
    # Add others as needed (transformed state might be handled differently)

class VisibilityType(Enum):
    PUBLIC = auto()
    HIDDEN_TO_OWNER = auto() # e.g., Morph
    HIDDEN_TO_ALL = auto()   # e.g., Face-down exiled card
    OWNER_ONLY = auto()     # e.g., Hand

class ZoneType(Enum):
    LIBRARY = auto()
    HAND = auto()
    BATTLEFIELD = auto()
    GRAVEYARD = auto()
    STACK = auto()
    EXILE = auto()
    COMMAND = auto()
    ANTE = auto() # Technically exists

class GameResult(Enum):
    WIN = auto()
    LOSS = auto()
    DRAW = auto()
    IN_PROGRESS = auto() 