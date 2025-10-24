"""
Tests for the zonk_players module.
Focuses on player decision making and strategy state changes.
"""

import pytest
import builtins
from project.assignment_4.zonk_players import Player, Human, Bot, Strategy
from project.assignment_4.zonk_config import BotStrategy, GamePhase
from project.assignment_4.zonk_dices import Dice, ScoreCalculator


def test_player_initialization():
    """Test player initialization with name and default values."""
    player = Bot("TestBot", BotStrategy.CONSERVATIVE)
    assert player.name == "TestBot"
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
    assert "TestBot" in representation
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

    assert result_conservative == False
    assert result_aggressive == False


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
            self.dice: Dice = Dice()
            self.current_round: int = 0
            self.game_over: bool = False
            self.final_round: bool = False
            self.players: list["Player"] = [bot]

    bot._game_ = SimpleGame()

    result_low_score = strategy.conservative_strategy(20, 6)
    result_high_score = strategy.conservative_strategy(100, 3)
    assert result_low_score == True
    assert result_high_score == False


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
            self.dice: Dice = Dice()
            self.current_round: int = 0
            self.game_over: bool = False
            self.final_round: bool = False
            self.players: list["Player"] = [bot]

    bot._game_ = SimpleGame()

    result_low_score = strategy.aggressive_strategy(50, 3)
    result_high_score = strategy.aggressive_strategy(300, 3)
    assert result_low_score == True
    assert result_high_score == False


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
            self.dice: Dice = Dice()
            self.game_over: bool = False
            self.final_round: bool = False
            self.players: list["Player"] = [bot]

    # Test early phase (should use conservative)
    bot._game_ = SimpleGame(2)
    early_result = strategy.adaptive_strategy(50, 3)

    # Test middle phase (should use aggressive)
    bot._game_ = SimpleGame(10)
    middle_result = strategy.adaptive_strategy(50, 3)

    # Test late phase (should use super aggressive)
    bot._game_ = SimpleGame(18)
    late_result = strategy.adaptive_strategy(50, 3)

    assert early_result == True
    assert middle_result == True
    assert late_result == True


def test_copycat_strategy_phase_changes():
    """Test copycat strategy changes with score changing."""
    copycat_bot = Bot("CopycatTestBot", BotStrategy.COPYCAT)
    copycat_strategy = Strategy(copycat_bot)

    conservative_bot = Bot("ConservativeTestBot", BotStrategy.CONSERVATIVE)
    conservative_strategy = Strategy(conservative_bot)

    aggressive_bot = Bot("AggressiveTestBot", BotStrategy.AGGRESSIVE)
    aggressive_strategy = Strategy(aggressive_bot)

    # Create minimal game with config
    class SimpleGame:
        def __init__(self):
            self.current_round = 0
            self.config = type(
                "Config",
                (),
                {"max_rounds": 20, "min_score_to_bank": 30, "max_rounds": 20},
            )()
            self.dice: Dice = Dice()
            self.game_over: bool = False
            self.final_round: bool = False
            self.players: list["Player"] = [
                copycat_bot,
                conservative_bot,
                aggressive_bot,
            ]

    copycat_bot._game_ = SimpleGame()

    conservative_result = conservative_strategy.conservative_strategy(200, 2)
    aggressive_result = aggressive_strategy.aggressive_strategy(100, 2)
    copycat_result = copycat_strategy.copycat_strategy(100, 2)
    assert conservative_result == False
    assert aggressive_result == True
    assert copycat_result == False

    conservative_result = conservative_strategy.conservative_strategy(100, 2)
    aggressive_result = aggressive_strategy.aggressive_strategy(120, 2)
    copycat_result = copycat_strategy.copycat_strategy(100, 2)
    assert conservative_result == False
    assert aggressive_result == True
    assert copycat_result == True
