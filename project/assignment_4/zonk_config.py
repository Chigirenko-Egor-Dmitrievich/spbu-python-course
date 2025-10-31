"""
Configuration module for the Zonk dice game.

This module defines enumerations for bot strategies and game phases,
as well as the main configuration class that holds game settings.
"""

from enum import Enum, auto


class BotStrategy(Enum):
    """Enumeration of possible bot strategies in the game."""

    CONSERVATIVE = auto()
    AGGRESSIVE = auto()
    SUPER_AGGRESSIVE = auto()
    ADAPTIVE = auto()
    COPYCAT = auto()


class GamePhase(Enum):
    """Enumeration of different phases during the game."""

    EARLY = auto()
    MIDDLE = auto()
    LATE = auto()


class GameConfig:
    """Configuration class that holds all game settings and parameters."""

    def __init__(self) -> None:
        """Initialize game configuration with default values."""

        self.target_score: int = 1000
        self.max_rounds: int = 20
        self.min_score_to_bank: int = 30
        self.zonk_penalty: int = -100
