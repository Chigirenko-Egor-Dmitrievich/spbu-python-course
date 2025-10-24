"""
Tests for the zonk_players module.
Focuses on player decision making and strategy state changes.
"""

import pytest
import builtins
from project.assignment_4.zonk_players import Player, Human, Bot, Strategy
from project.assignment_4.zonk_config import BotStrategy, GamePhase


def test_player_initialization():
    """Test player initialization with name and default values."""
    player = Bot("TestBot", BotStrategy.CONSERVATIVE)
    assert player.name == "TestPlayer"
    assert player.total_score == 0
    assert player.consecutive_zonks == 0
    assert player.is_active == True
    assert player._game_ is None


def test_player_set_game():
    """Test setting game reference for player."""
    player = Bot("TestBot", BotStrategy.CONSERVATIVE)

    # Create a minimal game-like object
    class SimpleGame:
        pass

    game = SimpleGame()
    player.set_game(game)
    assert player._game_ == game


def test_player_zonk_management():
    """Test zonk counter management."""
    player = Bot("TestBot", BotStrategy.CONSERVATIVE)

    # Initial state
    assert player.consecutive_zonks == 0

    # Add zonks
    player.add_zonk()
    assert player.consecutive_zonks == 1

    player.add_zonk()
    assert player.consecutive_zonks == 2

    # Reset counter
    player.reset_zonk_counter()
    assert player.consecutive_zonks == 0


def test_player_penalty_application():
    """Test penalty application logic."""
    player = Bot("TestBot", BotStrategy.CONSERVATIVE)
    player.total_score = 100

    # Apply penalty
    player.apply_penalty(-50)
    assert player.total_score == 50

    # Test that score doesn't go below zero
    player.apply_penalty(-100)
    assert player.total_score == 0


def test_player_string_representation():
    """Test player string representation."""
    player = Bot("TestBot", BotStrategy.CONSERVATIVE)
    player.total_score = 150
    player.consecutive_zonks = 2

    representation = str(player)
    assert "TestPlayer" in representation
    assert "150" in representation
    assert "2" in representation


def test_human_initialization():
    """Test human player initialization."""
    human = Human("TestHuman")
    assert human.name == "TestHuman"
    assert human.total_score == 0


def test_bot_initialization():
    """Test bot initialization with strategy."""
    bot = Bot("TestBot", BotStrategy.CONSERVATIVE)
    assert bot.name == "TestBot"
    assert bot.strategy_type == BotStrategy.CONSERVATIVE
    assert isinstance(bot.strategy, Strategy)


def test_strategy_initialization():
    """Test strategy initialization with bot reference."""
    bot = Bot("TestBot", BotStrategy.CONSERVATIVE)
    strategy = Strategy(bot)
    assert strategy.bot == bot


def test_strategy_routing():
    """Test that strategy routes to correct methods."""
    bot = Bot("TestBot", BotStrategy.CONSERVATIVE)
    strategy = Strategy(bot)

    # Conservative strategy should be more cautious
    result_conservative = strategy.make_strategy(BotStrategy.CONSERVATIVE, 100, 3)
    result_aggressive = strategy.make_strategy(BotStrategy.AGGRESSIVE, 100, 3)

    assert isinstance(result_conservative, bool)
    assert isinstance(result_aggressive, bool)


def test_game_phase_detection():
    """Test game phase detection logic."""
    bot = Bot("TestBot", BotStrategy.CONSERVATIVE)
    strategy = Strategy(bot)

    # Create a minimal game simulation
    class SimpleGame:
        def __init__(self, current_round, max_rounds=20):
            self.current_round = current_round
            self.config = type("Config", (), {"max_rounds": max_rounds})()

    # Test early phase
    bot._game_ = SimpleGame(5)  # 25% of 20 rounds
    phase = strategy.get_game_phase()
    assert phase == GamePhase.EARLY

    # Test middle phase
    bot._game_ = SimpleGame(10)  # 50% of 20 rounds
    phase = strategy.get_game_phase()
    assert phase == GamePhase.MIDDLE

    # Test late phase
    bot._game_ = SimpleGame(18)  # 90% of 20 rounds
    phase = strategy.get_game_phase()
    assert phase == GamePhase.LATE

    # Test no game case
    bot._game_ = None
    phase = strategy.get_game_phase()
    assert phase == GamePhase.MIDDLE


def test_conservative_strategy_decisions():
    """Test conservative strategy decision making."""
    bot = Bot("TestBot", BotStrategy.CONSERVATIVE)
    strategy = Strategy(bot)

    # Create minimal game with config
    class SimpleGame:
        def __init__(self):
            self.config = type(
                "Config", (), {"min_score_to_bank": 30, "max_rounds": 20}
            )()

    bot._game_ = SimpleGame()

    # Test case: high score -> should bank
    result_high_score = strategy.conservative_strategy(100, 3)
    # Conservative should bank at high scores
    assert result_high_score == False

    # Test case: low score with many dice -> should continue
    result_low_score = strategy.conservative_strategy(20, 6)
    # Conservative might continue with many dice and low score
    assert isinstance(result_low_score, bool)


def test_aggressive_strategy_decisions():
    """Test aggressive strategy decision making."""
    bot = Bot("TestBot", BotStrategy.AGGRESSIVE)
    strategy = Strategy(bot)

    # Create minimal game with config
    class SimpleGame:
        def __init__(self):
            self.config = type(
                "Config", (), {"min_score_to_bank": 30, "max_rounds": 20}
            )()

    bot._game_ = SimpleGame()

    # Aggressive strategy should be more likely to continue
    result = strategy.aggressive_strategy(50, 3)
    assert isinstance(result, bool)


def test_adaptive_strategy_phase_changes():
    """Test adaptive strategy changes with game phase."""
    bot = Bot("TestBot", BotStrategy.ADAPTIVE)
    strategy = Strategy(bot)

    # Create game simulation for different phases
    class SimpleGame:
        def __init__(self, current_round):
            self.current_round = current_round
            self.config = type(
                "Config",
                (),
                {"max_rounds": 20, "min_score_to_bank": 30, "max_rounds": 20},
            )()

    # Test early phase (should use conservative)
    bot._game_ = SimpleGame(2)
    early_result = strategy.adaptive_strategy(50, 3)

    # Test middle phase (should use aggressive)
    bot._game_ = SimpleGame(10)
    middle_result = strategy.adaptive_strategy(50, 3)

    # Test late phase (should use super aggressive)
    bot._game_ = SimpleGame(18)
    late_result = strategy.adaptive_strategy(50, 3)

    # All should be boolean decisions
    assert isinstance(early_result, bool)
    assert isinstance(middle_result, bool)
    assert isinstance(late_result, bool)
