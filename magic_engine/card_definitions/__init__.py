"""Initializes the card definitions module."""

from .basic_lands import PlainsData, ForestData # Keep existing
from .creatures_white import SavannahLionsData # Add white creature
from .creatures_green import GrizzlyBearsData # Add green creature

__all__ = [
    "PlainsData",
    "ForestData",
    "SavannahLionsData",
    "GrizzlyBearsData",
] 