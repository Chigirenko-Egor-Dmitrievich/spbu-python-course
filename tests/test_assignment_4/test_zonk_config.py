"""
Tests for the zonk_config module.
Focuses on configuration validation and enum functionality.
"""

import pytest
from project.assignment_4.zonk_config import BotStrategy, GamePhase, GameConfig


def test_bot_strategy_values():
    """Test that all bot strategies are properly defined."""
    strategies = list(BotStrategy)
    expected_strategies = [
        BotStrategy.CONSERVATIVE,
        BotStrategy.AGGRESSIVE,
        BotStrategy.SUPER_AGGRESSIVE,
        BotStrategy.ADAPTIVE,
        BotStrategy.COPYCAT,
    ]
    assert strategies == expected_strategies


def test_game_phase_values():
    """Test that all game phases are properly defined."""
    phases = list(GamePhase)
    expected_phases = [GamePhase.EARLY, GamePhase.MIDDLE, GamePhase.LATE]
    assert phases == expected_phases


def test_default_configuration():
    """Test that default configuration values are set correctly."""
    config = GameConfig()
    assert config.target_score == 1000
    assert config.max_rounds == 20
    assert config.min_score_to_bank == 30
    assert config.zonk_penalty == -100


def test_configuration_modification():
    """Test that configuration can be modified and state changes."""
    config = GameConfig()

    # Store initial state
    initial_target = config.target_score

    # Modify configuration
    config.target_score = 1500
    config.max_rounds = 15
    config.min_score_to_bank = 50

    # Verify state changed
    assert config.target_score == 1500
    assert config.max_rounds == 15
    assert config.min_score_to_bank == 50
    assert config.target_score != initial_target
