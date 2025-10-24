"""
Tests for the zonk_players module.
Focuses on player decision making and strategy state changes.
"""

import pytest
from unittest.mock import Mock, patch
from project.assignment_4.zonk_players import Player, Human, Bot, Strategy
from project.assignment_4.zonk_config import BotStrategy, GamePhase


class TestPlayer:
    """Test base Player class functionality."""

    def test_player_initialization(self):
        """Test player initialization with name and default values."""
        player = Player("TestPlayer")
        assert player.name == "TestPlayer"
        assert player.total_score == 0
        assert player.consecutive_zonks == 0
        assert player.is_active == True
        assert player._game_ is None

    def test_player_set_game(self):
        """Test setting game reference for player."""
        player = Player("TestPlayer")
        mock_game = Mock()

        player.set_game(mock_game)
        assert player._game_ == mock_game

    def test_player_zonk_management(self):
        """Test zonk counter management."""
        player = Player("TestPlayer")

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

    def test_player_penalty_application(self):
        """Test penalty application logic."""
        player = Player("TestPlayer")
        player.total_score = 100

        # Apply penalty
        player.apply_penalty(-50)
        assert player.total_score == 50

        # Test that score doesn't go below zero
        player.apply_penalty(-100)
        assert player.total_score == 0

    def test_player_string_representation(self):
        """Test player string representation."""
        player = Player("TestPlayer")
        player.total_score = 150
        player.consecutive_zonks = 2

        representation = str(player)
        assert "TestPlayer" in representation
        assert "150" in representation
        assert "2" in representation


class TestHuman:
    """Test Human player class functionality."""

    @patch("builtins.input")
    def test_human_decision_yes(self, mock_input):
        """Test human decision to continue rolling."""
        mock_input.return_value = "y"
        human = Human("TestHuman")
        human._game_ = Mock()
        human._game_.config.min_score_to_bank = 30

        decision = human.make_decision(50, 3)
        assert decision == True

    @patch("builtins.input")
    def test_human_decision_no_with_sufficient_score(self, mock_input):
        """Test human decision to bank sufficient score."""
        mock_input.return_value = "n"
        human = Human("TestHuman")
        human._game_ = Mock()
        human._game_.config.min_score_to_bank = 30

        decision = human.make_decision(50, 3)
        assert decision == False

    @patch("builtins.input")
    def test_human_decision_insufficient_score(self, mock_input):
        """Test human forced to continue with insufficient score."""
        mock_input.side_effect = ["n", "y"]  # First try to stop, then continue
        human = Human("TestHuman")
        human._game_ = Mock()
        human._game_.config.min_score_to_bank = 30

        decision = human.make_decision(20, 3)
        assert decision == True


class TestBot:
    """Test Bot player class functionality."""

    def test_bot_initialization(self):
        """Test bot initialization with strategy."""
        bot = Bot("TestBot", BotStrategy.CONSERVATIVE)
        assert bot.name == "TestBot"
        assert bot.strategy_type == BotStrategy.CONSERVATIVE
        assert isinstance(bot.strategy, Strategy)

    def test_bot_decision_delegation(self):
        """Test that bot delegates decisions to strategy."""
        bot = Bot("TestBot", BotStrategy.CONSERVATIVE)
        bot.strategy._conservative_strategy = Mock(return_value=True)

        decision = bot.make_decision(50, 3)
        assert decision == True
        bot.strategy._conservative_strategy.assert_called_once_with(50, 3)


class TestStrategy:
    """Test Strategy class functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.bot = Bot("TestBot", BotStrategy.CONSERVATIVE)
        self.strategy = Strategy(self.bot)

    def test_strategy_initialization(self):
        """Test strategy initialization with bot reference."""
        assert self.strategy.bot == self.bot

    def test_strategy_routing(self):
        """Test that strategy routes to correct methods."""
        # Test conservative strategy routing
        self.strategy._conservative_strategy = Mock(return_value=True)
        result = self.strategy.make_strategy(BotStrategy.CONSERVATIVE, 50, 3)
        assert result == True
        self.strategy._conservative_strategy.assert_called_once_with(50, 3)

        # Test aggressive strategy routing
        self.strategy._aggressive_strategy = Mock(return_value=False)
        result = self.strategy.make_strategy(BotStrategy.AGGRESSIVE, 50, 3)
        assert result == False
        self.strategy._aggressive_strategy.assert_called_once_with(50, 3)

    def test_game_phase_detection(self):
        """Test game phase detection logic."""
        # Mock game setup
        mock_game = Mock()
        mock_game.config.max_rounds = 20
        mock_game.current_round = 5  # Early phase (25%)
        self.bot._game_ = mock_game

        phase = self.strategy._get_game_phase()
        assert phase == GamePhase.EARLY

        # Test middle phase
        mock_game.current_round = 10  # Middle phase (50%)
        phase = self.strategy._get_game_phase()
        assert phase == GamePhase.MIDDLE

        # Test late phase
        mock_game.current_round = 18  # Late phase (90%)
        phase = self.strategy._get_game_phase()
        assert phase == GamePhase.LATE

        # Test no game case
        self.bot._game_ = None
        phase = self.strategy._get_game_phase()
        assert phase == GamePhase.MIDDLE

    def test_leader_detection(self):
        """Test leader position detection."""
        mock_game = Mock()
        mock_game.config.min_score_to_bank = 30

        # Create mock players
        leader = Mock()
        leader.total_score = 200
        leader.__ne__ = Mock(return_value=True)  # For != comparison

        self.bot.total_score = 100
        mock_game.players = [self.bot, leader]

        self.bot._game_ = mock_game

        # Bot is behind leader (100 < 200 - 90)
        assert self.strategy._is_behind_leader() == True

        # Bot is not far behind (100 > 200 - 300)
        assert self.strategy._is_far_behind_leader() == False

    def test_conservative_strategy_state_changes(self):
        """Test conservative strategy decision making with state changes."""
        # Test case: high score -> bank
        result = self.strategy._conservative_strategy(100, 3)
        assert result == False  # Should bank at 100 points

        # Test case: low score with many dice -> continue
        result = self.strategy._conservative_strategy(20, 6)
        assert result == True  # Should continue with 6 dice

    def test_adaptive_strategy_state_changes(self):
        """Test adaptive strategy changes with game phase."""
        mock_game = Mock()
        mock_game.config.max_rounds = 20
        self.bot._game_ = mock_game

        # Early game should use conservative strategy
        mock_game.current_round = 2
        self.strategy._conservative_strategy = Mock(return_value=True)
        self.strategy._aggressive_strategy = Mock(return_value=False)

        result = self.strategy._adaptive_strategy(50, 3)
        self.strategy._conservative_strategy.assert_called_once_with(50, 3)
        assert result == True
