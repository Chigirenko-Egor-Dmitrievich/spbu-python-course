"""
Tests for the zonk_game module.
Focuses on game state changes over time and turn/round management.
"""

import pytest
from unittest.mock import Mock, patch
from project.assignment_4.zonk_game import Turn, Game
from project.assignment_4.zonk_players import Bot
from project.assignment_4.zonk_config import BotStrategy, GameConfig


class TestTurn:
    """Test Turn class functionality and state changes."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_player = Mock()
        self.mock_player.name = "TestPlayer"
        self.mock_player.total_score = 0
        self.mock_player.consecutive_zonks = 0
        self.mock_player.add_zonk = Mock()

        self.mock_dice = Mock()
        self.turn = Turn(self.mock_player, self.mock_dice)

    def test_turn_initialization(self):
        """Test turn initialization with proper state."""
        assert self.turn.player == self.mock_player
        assert self.turn.dice == self.mock_dice
        assert self.turn.current_score == 0
        assert self.turn.is_zonk == False
        assert self.turn.used_dice == []

    @patch("zonk_game.ScoreCalculator.calculate_score")
    def test_successful_turn_accumulation(self, mock_calculate):
        """Test successful turn with score accumulation."""
        # Mock dice rolls and score calculations
        self.mock_dice.roll.side_effect = [
            [1, 1, 1, 2, 3, 4],  # First roll: 100 points
            [5, 5, 2, 3, 4],  # Second roll: 10 points
        ]
        mock_calculate.side_effect = [
            (100, [1, 1, 1]),  # First calculation
            (10, [5, 5]),  # Second calculation
        ]

        # Mock player decision to stop after second roll
        self.mock_player.make_decision.side_effect = [True, False]
        self.mock_player.total_score = 0

        result = self.turn.play()

        # Verify turn results
        assert result == 110  # 100 + 10
        assert self.turn.current_score == 110
        assert self.turn.is_zonk == False
        assert self.mock_player.total_score == 0  # Not added yet

    @patch("zonk_game.ScoreCalculator.calculate_score")
    def test_zonk_turn(self, mock_calculate):
        """Test turn ending with zonk."""
        self.mock_dice.roll.return_value = [2, 3, 4, 6, 2, 3]
        mock_calculate.return_value = (0, [])  # Zonk

        result = self.turn.play()

        assert result == 0
        assert self.turn.is_zonk == True
        self.mock_player.add_zonk.assert_called_once()

    @patch("zonk_game.ScoreCalculator.calculate_score")
    def test_555_rule_trigger(self, mock_calculate):
        """Test 555 rule triggering."""
        self.mock_player.total_score = 500
        self.mock_dice.roll.return_value = [1, 1, 1, 2, 3, 4]  # 100 points
        mock_calculate.return_value = (100, [1, 1, 1])

        # Player would reach 600 total, but we test 555 rule check
        self.mock_player.make_decision.return_value = False

        # Mock the 555 rule to return True
        with patch.object(self.turn, "_check_555_rule", return_value=True):
            result = self.turn.play()

        assert result == 0
        assert self.mock_player.total_score == 0

    def test_555_rule_detection(self):
        """Test 555 rule detection logic."""
        self.mock_player.total_score = 455
        self.turn.current_score = 100  # Would make 555 total

        result = self.turn.check_555_rule()

        assert result == True
        assert self.mock_player.total_score == 0

    def test_555_rule_no_trigger(self):
        """Test 555 rule not triggering with normal score."""
        self.mock_player.total_score = 400
        self.turn.current_score = 100  # Makes 500 total

        result = self.turn.check_555_rule()

        assert result == False
        assert self.mock_player.total_score == 400


class TestGame:
    """Test Game class functionality and state progression."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = GameConfig()
        self.config.target_score = 1000
        self.config.max_rounds = 5
        self.config.min_score_to_bank = 30
        self.config.zonk_penalty = -100

        self.game = Game(self.config)

    def test_game_initialization(self):
        """Test game initialization with proper state."""
        assert game.config == self.config
        assert isinstance(game.dice, Dice)
        assert game.players == []
        assert game.current_round == 0
        assert game.game_over == False
        assert game.final_round == False

    def test_add_player(self):
        """Test adding players to the game."""
        mock_player = Mock()

        self.game.add_player(mock_player)

        assert len(self.game.players) == 1
        assert self.game.players[0] == mock_player
        mock_player.set_game.assert_called_once_with(self.game)

    @patch("zonk_game.Turn")
    def test_play_round_state_progression(self, mock_turn):
        """Test that game state progresses during a round."""
        # Setup mock players
        player1 = Mock()
        player1.name = "Player1"
        player1.is_active = True
        player1.total_score = 0
        player1.consecutive_zonks = 0
        player1.reset_zonk_counter = Mock()

        player2 = Mock()
        player2.name = "Player2"
        player2.is_active = True
        player2.total_score = 0
        player2.consecutive_zonks = 0
        player2.reset_zonk_counter = Mock()

        self.game.players = [player1, player2]

        # Setup mock turn
        mock_turn_instance = Mock()
        mock_turn_instance.play.return_value = 50  # Successful turn
        mock_turn_instance.is_zonk = False
        mock_turn.return_value = mock_turn_instance

        # Store initial state
        initial_round = self.game.current_round

        # Play round
        self.game.play_round()

        # Verify state changes
        assert self.game.current_round == initial_round + 1
        assert player1.total_score == 50
        player1.reset_zonk_counter.assert_called_once()

    @patch("zonk_game.Turn")
    def test_three_consecutive_zonks_penalty(self, mock_turn):
        """Test penalty application for three consecutive zonks."""
        player = Mock()
        player.name = "TestPlayer"
        player.is_active = True
        player.total_score = 200
        player.consecutive_zonks = 3  # Three consecutive zonks
        player.reset_zonk_counter = Mock()
        player.apply_penalty = Mock()

        self.game.players = [player]

        # Setup zonk turn
        mock_turn_instance = Mock()
        mock_turn_instance.play.return_value = 0
        mock_turn_instance.is_zonk = True
        mock_turn.return_value = mock_turn_instance

        self.game.play_round()

        # Verify penalty applied
        player.apply_penalty.assert_called_once_with(self.config.zonk_penalty)
        player.reset_zonk_counter.assert_called_once()

    def test_win_conditions_target_score(self):
        """Test win condition detection for target score."""
        player = Mock()
        player.total_score = 1000  # Exactly target score
        self.game.players = [player]

        result = self.game.check_win_conditions()

        assert result == True
        assert self.game.final_round == True
        assert self.game.game_over == True

    def test_win_conditions_max_rounds(self):
        """Test win condition detection for max rounds."""
        self.game.current_round = 5  # Max rounds
        self.game.config.max_rounds = 5

        result = self.game.check_win_conditions()

        assert result == True
        assert self.game.game_over == True

    def test_winner_determination(self):
        """Test winner determination logic."""
        # Setup players with different scores
        player1 = Mock()
        player1.name = "Player1"
        player1.total_score = 1200
        player1.is_active = True

        player2 = Mock()
        player2.name = "Player2"
        player2.total_score = 1100
        player2.is_active = True

        self.game.players = [player1, player2]
        self.game.game_over = True

        winner = self.game.get_winner()

        assert winner == player1
        assert winner.total_score == 1200

    def test_game_state_progression_over_time(self):
        """Comprehensive test of game state progression over multiple rounds."""
        # Setup simple bot players
        bot1 = Bot("Bot1", BotStrategy.CONSERVATIVE)
        bot2 = Bot("Bot2", BotStrategy.AGGRESSIVE)

        self.game.add_player(bot1)
        self.game.add_player(bot2)

        # Store initial state
        initial_round = self.game.current_round
        initial_game_over = self.game.game_over

        # Play one round and check state progression
        with patch.object(self.game, "play_round") as mock_play_round:
            self.game.play_round()
            mock_play_round.assert_called_once()

        # Verify state changed
        assert self.game.current_round == initial_round + 1

        # Simulate game progression until completion
        self.game.current_round = self.config.max_rounds

        win_detected = self.game.check_win_conditions()
        assert win_detected == True
        assert self.game.game_over == True
        assert self.game.game_over != initial_game_over

    def test_final_round_mechanism(self):
        """Test final round triggering mechanism."""
        player = Mock()
        player.total_score = 1000  # Reaches target score
        self.game.players = [player]

        # First time reaching target - should trigger final round
        result1 = self.game.check_win_conditions()
        assert result1 == False  # Not immediate win
        assert self.game.final_round == True
        assert self.game.game_over == False

        # Second check after final round - should end game
        result2 = self.game.check_win_conditions()
        assert result2 == True
        assert self.game.game_over == True
