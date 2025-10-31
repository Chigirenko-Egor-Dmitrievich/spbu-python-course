"""
Main module for the ZONK dice game.

This module provides the entry point for the game, allowing configuration
and setup of players before starting the main game loop.
"""

from project.assignment_4.zonk_game import Game
from project.assignment_4.zonk_players import Bot, Human
from project.assignment_4.zonk_config import BotStrategy, GameConfig


def main() -> None:
    """
    Main function to set up and run the ZONK game.

    Creates game configuration, initializes players (both bots and humans),
    and starts the game. This is the primary entry point for the application.
    """

    # Creating a configuration
    config = GameConfig()
    config.target_score = 1000
    config.max_rounds = 20
    config.min_score_to_bank = 30

    # Creating a game
    game = Game(config)

    # Adding players
    game.add_player(Bot("Conservative", BotStrategy.CONSERVATIVE))
    game.add_player(Bot("Aggressive", BotStrategy.AGGRESSIVE))
    game.add_player(Bot("Super_aggressive", BotStrategy.SUPER_AGGRESSIVE))
    game.add_player(Bot("Adaptive", BotStrategy.ADAPTIVE))
    game.add_player(Bot("Copycat", BotStrategy.COPYCAT))
    # game.add_player(Human("Egor"))
    # game.add_player(Human("Pavel Alimov"))

    # Launching the game
    game.play_game()


if __name__ == "__main__":
    main()
