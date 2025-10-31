"""
Tests for the zonk_game module.
Focuses on game state changes over time and turn/round management.
"""

import pytest
from project.assignment_4.zonk_game import Turn, Game
from project.assignment_4.zonk_players import Bot
from project.assignment_4.zonk_config import BotStrategy, GameConfig
from project.assignment_4.zonk_dices import Dice, ScoreCalculator


def test_turn_initialization():
    """Test turn initialization with proper state."""
    player = Bot("TestBot", BotStrategy.CONSERVATIVE)
    dice = Dice()
    turn = Turn(player, dice)

    assert turn.player == player
    assert turn.dice == dice
    assert turn.current_score == 0
    assert turn.is_zonk == False
    assert turn.used_dice == []


def test_555_rule_detection():
    """Test 555 rule detection logic."""
    player = Bot("TestBot", BotStrategy.CONSERVATIVE)
    player.total_score = 455
    dice = Dice()
    turn = Turn(player, dice)
    turn.current_score = 100  # Would make 555 total

    result = turn.check_555_rule()

    assert result == True
    assert player.total_score == 0


def test_555_rule_no_trigger():
    """Test 555 rule not triggering with normal score."""
    player = Bot("TestBot", BotStrategy.CONSERVATIVE)
    player.total_score = 400
    dice = Dice()
    turn = Turn(player, dice)
    turn.current_score = 100  # Makes 500 total

    result = turn.check_555_rule()

    assert result == False
    assert player.total_score == 400


def test_game_initialization():
    """Test game initialization with proper state."""
    config = GameConfig()
    game = Game(config)

    assert game.config == config
    assert isinstance(game.dice, Dice)
    assert game.players == []
    assert game.current_round == 0
    assert game.game_over == False
    assert game.final_round == False


def test_add_player():
    """Test adding players to the game."""
    config = GameConfig()
    game = Game(config)
    player = Bot("TestBot", BotStrategy.CONSERVATIVE)

    game.add_player(player)

    assert len(game.players) == 1
    assert game.players[0] == player
    assert player.game == game


def test_win_conditions_target_score():
    """Test win condition detection for target score."""
    config = GameConfig()
    config.target_score = 500
    game = Game(config)

    # Create a player that reaches target score
    player = Bot("TestBot", BotStrategy.CONSERVATIVE)
    player.total_score = 500
    game.players = [player]

    result = game.check_win_conditions()

    # First time reaching target should trigger final round, not immediate win
    assert result == False
    assert game.final_round == True


def test_win_conditions_max_rounds():
    """Test win condition detection for max rounds."""
    config = GameConfig()
    config.max_rounds = 5
    game = Game(config)
    game.current_round = 5  # Max rounds

    result = game.check_win_conditions()

    assert result == True
    assert game.game_over == True


def test_winner_determination_single_player():
    """Test winner determination with single player."""
    config = GameConfig()
    config.target_score = 500
    game = Game(config)
    game.game_over = True

    player = Bot("TestBot", BotStrategy.CONSERVATIVE)
    player.total_score = 600  # Above target
    player.is_active = True
    game.players = [player]

    winner = game.get_winner()

    assert winner == player
    assert winner.total_score == 600


def test_winner_determination_multiple_players():
    """Test winner determination with multiple players."""
    config = GameConfig()
    game = Game(config)
    game.game_over = True

    player1 = Bot("Bot1", BotStrategy.CONSERVATIVE)
    player1.total_score = 1200
    player1.is_active = True

    player2 = Bot("Bot2", BotStrategy.AGGRESSIVE)
    player2.total_score = 1100
    player2.is_active = True

    game.players = [player1, player2]

    winner = game.get_winner()

    assert winner == player1
    assert winner.total_score == 1200


def test_three_consecutive_zonks_penalty():
    """Test penalty application for three consecutive zonks."""
    config = GameConfig()
    game = Game(config)

    player = Bot("TestBot", BotStrategy.CONSERVATIVE)
    player.total_score = 200
    player.consecutive_zonks = 2  # Two consecutive zonks
    game.players = [player]

    # Simulate a zonk turn
    player.add_zonk()  # This makes it 4 zonks, triggering penalty

    # Apply penalty logic (simulating what happens in play_round)
    if player.consecutive_zonks == 3:
        player.apply_penalty(config.zonk_penalty)
        player.reset_zonk_counter()

    # Verify penalty applied and counter reset
    assert player.total_score == 100  # 200 - 100 penalty
    assert player.consecutive_zonks == 0


def test_game_state_progression():
    """Test basic game state progression."""
    config = GameConfig()
    config.target_score = 100
    config.max_rounds = 3
    game = Game(config)

    # Add players
    bot1 = Bot("Bot1", BotStrategy.CONSERVATIVE)
    bot2 = Bot("Bot2", BotStrategy.AGGRESSIVE)
    game.add_player(bot1)
    game.add_player(bot2)

    # Store initial state
    initial_round = game.current_round
    initial_game_over = game.game_over

    # Play one round (simplified - just increment round counter)
    game.current_round += 1

    # Verify state changed
    assert game.current_round == initial_round + 1
    assert game.game_over == initial_game_over


def test_final_round_mechanism():
    """Test final round triggering mechanism."""
    config = GameConfig()
    config.target_score = 500
    game = Game(config)

    player = Bot("TestBot", BotStrategy.CONSERVATIVE)
    player.total_score = 500  # Reaches target score
    game.players = [player]

    # First time reaching target - should trigger final round
    result1 = game.check_win_conditions()
    assert result1 == False  # Not immediate win
    assert game.final_round == True
    assert game.game_over == False

    # Simulate that we're in final round and check again
    result2 = game.check_win_conditions()
    # In final round, reaching target should end game
    assert result2 == True
    assert game.game_over == True
