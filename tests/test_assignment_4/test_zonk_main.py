"""
Tests for the zonk_main module.
Focuses on game initialization and execution flow.
"""

import pytest
from unittest.mock import Mock, patch
from project.assignment_4.zonk_main import main


class TestZonkMain:
    """Test main game execution functionality."""

    @patch("zonk_main.Game")
    @patch("zonk_main.GameConfig")
    @patch("zonk_main.Bot")
    @patch("zonk_main.BotStrategy")
    def test_main_function_execution(
        self, mock_strategy, mock_bot, mock_config, mock_game
    ):
        """Test that main function executes all necessary steps."""
        # Mock the game configuration
        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance

        # Mock the game instance
        mock_game_instance = Mock()
        mock_game.return_value = mock_game_instance

        # Mock bot instances
        mock_bot_instances = [Mock() for _ in range(5)]
        mock_bot.side_effect = mock_bot_instances

        # Execute main function
        main()

        # Verify configuration was created and modified
        mock_config.assert_called_once()
        assert mock_config_instance.target_score == 1000
        assert mock_config_instance.max_rounds == 20
        assert mock_config_instance.min_score_to_bank == 30

        # Verify game was created with config
        mock_game.assert_called_once_with(mock_config_instance)

        # Verify players were added
        assert mock_game_instance.add_player.call_count == 5

        # Verify game was played
        mock_game_instance.play_game.assert_called_once()

    def test_main_module_execution(self):
        """Test that main module can be executed directly."""
        # This test verifies that the main module doesn't crash when executed
        # We'll mock all the dependencies to avoid actual game execution
        with patch("zonk_main.Game") as mock_game, patch(
            "zonk_main.GameConfig"
        ) as mock_config, patch("zonk_main.Bot") as mock_bot:

            # Set up mocks
            mock_game_instance = Mock()
            mock_game.return_value = mock_game_instance

            # Execute main function
            main()

            # Verify the game flow was initiated
            mock_game_instance.play_game.assert_called_once()
