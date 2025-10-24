"""
Players module for the ZONK dice game.

This module defines the player classes, including human players and various
bot strategies with different decision-making algorithms for the game.
"""

from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING
from project.assignment_4.zonk_config import BotStrategy, GamePhase

if TYPE_CHECKING:
    from project.assignment_4.zonk_game import Game


class Player(ABC):
    """Abstract base class representing a player in the game."""

    def __init__(self, name: str) -> None:
        """
        Initialize a player.

        Args:
            name: The player's name
        """

        self.name: str = name
        self.total_score: int = 0
        self.consecutive_zonks: int = 0
        self.is_active: bool = True
        self._game_: Optional["Game"] = None

    def set_game(self, game: "Game") -> None:
        """
        Set the game reference for the player.

        Args:
            game: The game instance this player belongs to
        """

        self._game_ = game

    @abstractmethod
    def make_decision(self, current_turn_score: int, remaining_dice: int) -> bool:
        """
        Make a decision whether to continue rolling or bank points.

        Args:
            current_turn_score: Current score accumulated in this turn
            remaining_dice: Number of dice remaining to roll

        Returns:
            True if player decides to continue rolling, False to bank points
        """

        pass

    def reset_zonk_counter(self) -> None:
        """Reset the consecutive zonk counter to zero."""

        self.consecutive_zonks = 0

    def add_zonk(self) -> None:
        """Increment the consecutive zonk counter by one."""

        self.consecutive_zonks += 1

    def apply_penalty(self, penalty: int) -> None:
        """
        Apply a penalty to the player's total score.

        Args:
            penalty: The penalty points to subtract (negative number)
        """

        self.total_score += penalty
        if self.total_score < 0:
            self.total_score = 0

    def __str__(self) -> str:
        """
        Return string representation of the player.

        Returns:
            String with player name, score and zonk count
        """

        return f"{self.name}: {self.total_score} points (consecutive zonks: {self.consecutive_zonks})"


class Human(Player):
    """Human player class that gets decisions from user input."""

    def __init__(self, name: str) -> None:
        """
        Initialize a human player.

        Args:
            name: The player's name
        """

        super().__init__(name)

    def make_decision(self, current_turn_score: int, remaining_dice: int) -> bool:
        """
        Get decision from human player via console input.

        Args:
            current_turn_score: Current score accumulated in this turn
            remaining_dice: Number of dice remaining to roll

        Returns:
            True if player decides to continue rolling, False to bank points
        """

        while True:
            try:
                choice = input("Continue to roll? (y - yes, n - no): ").lower().strip()
                print()
                if choice in ["д", "да", "y", "yes"]:
                    return True
                elif choice in ["н", "нет", "n", "no"]:

                    if self._game_ is None:
                        # Default behavior if game is not set
                        return current_turn_score < 30

                    # Checking for minimum score before banking
                    if current_turn_score >= self._game_.config.min_score_to_bank:
                        return False
                    else:
                        print(
                            f"You can't stop now! You need at least {self._game_.config.min_score_to_bank} points, your current score is {current_turn_score} points"
                        )
                        continue
                else:
                    print("Please enter 'y' to continue or 'n' to stop")

            except EOFError:
                # If the input is completed, act like a very conservative bot.
                return current_turn_score < 100
            except KeyboardInterrupt:
                print("\nThe game was interrupted by the user")
                exit()


class Bot(Player):
    """Bot player class that uses strategies for automated decision making."""

    def __init__(self, name: str, strategy_type: BotStrategy) -> None:
        """
        Initialize a bot player with a specific strategy.

        Args:
            name: The bot's name
            strategy_type: The strategy type this bot will use
        """

        super().__init__(name)
        self.strategy_type: BotStrategy = strategy_type
        self.strategy: Strategy = Strategy(self)

    def make_decision(self, current_turn_score: int, remaining_dice: int) -> bool:
        """
        Delegate decision making to the bot's strategy.

        Args:
            current_turn_score: Current score accumulated in this turn
            remaining_dice: Number of dice remaining to roll

        Returns:
            True if bot decides to continue rolling, False to bank points
        """

        return self.strategy.make_strategy(
            self.strategy_type, current_turn_score, remaining_dice
        )


class Strategy:
    """Strategy class implementing different decision-making algorithms for bots."""

    def __init__(self, bot: Bot) -> None:
        """
        Initialize strategy for a bot.

        Args:
            bot: The bot instance this strategy belongs to
        """

        self.bot: Bot = bot

    def make_strategy(
        self, strategy_type: BotStrategy, current_turn_score: int, remaining_dice: int
    ) -> bool:
        """
        Execute the appropriate strategy based on the bot's strategy type.

        Args:
            strategy_type: The strategy type to use
            current_turn_score: Current score accumulated in this turn
            remaining_dice: Number of dice remaining to roll

        Returns:
            True if strategy decides to continue rolling, False to bank points
        """

        if strategy_type == BotStrategy.CONSERVATIVE:
            return self.conservative_strategy(current_turn_score, remaining_dice)
        elif strategy_type == BotStrategy.AGGRESSIVE:
            return self.aggressive_strategy(current_turn_score, remaining_dice)
        elif strategy_type == BotStrategy.SUPER_AGGRESSIVE:
            return self.super_aggressive_strategy(current_turn_score, remaining_dice)
        elif strategy_type == BotStrategy.ADAPTIVE:
            return self.adaptive_strategy(current_turn_score, remaining_dice)
        elif strategy_type == BotStrategy.COPYCAT:
            return self.copycat_strategy(current_turn_score, remaining_dice)
        else:
            return self.conservative_strategy(current_turn_score, remaining_dice)

    def get_game_phase(self) -> GamePhase:
        """
        Determine the current phase of the game.

        Returns:
            Current game phase (EARLY, MIDDLE, or LATE)
        """

        if not self.bot._game_:
            return GamePhase.MIDDLE
        total_rounds: int = self.bot._game_.config.max_rounds
        current_round: int = self.bot._game_.current_round

        if current_round <= total_rounds * 0.3:
            return GamePhase.EARLY
        elif current_round <= total_rounds * 0.7:
            return GamePhase.MIDDLE
        else:
            return GamePhase.LATE

    def is_behind_leader(self) -> bool:
        """
        Check if the bot is behind the leader.

        Returns:
            True if bot is behind leader by more than 3x minimum bank score
        """

        if not self.bot._game_ or len(self.bot._game_.players) <= 1:
            return False

        min_score: int = self.bot._game_.config.min_score_to_bank
        max_score: int = max(
            p.total_score for p in self.bot._game_.players if p != self.bot
        )
        return self.bot.total_score < max_score - min_score * 3

    def is_far_behind_leader(self) -> bool:
        """
        Check if the bot is significantly behind the leader.

        Returns:
            True if bot is behind leader by more than 10x minimum bank score
        """

        if not self.bot._game_ or len(self.bot._game_.players) <= 1:
            return False

        min_score: int = self.bot._game_.config.min_score_to_bank
        max_score: int = max(
            p.total_score for p in self.bot._game_.players if p != self.bot
        )
        return self.bot.total_score < max_score - min_score * 10

    # Basic strategies:
    def conservative_strategy(
        self, current_turn_score: int, remaining_dice: int
    ) -> bool:
        """
        Conservative strategy - banks points early and avoids risks.

        Args:
            current_turn_score: Current score accumulated in this turn
            remaining_dice: Number of dice remaining to roll

        Returns:
            True to continue rolling, False to bank points
        """

        game_phase: GamePhase = self.get_game_phase()
        is_behind: bool = self.is_behind_leader()
        min_score: int = (
            30 if self.bot._game_ is None else self.bot._game_.config.min_score_to_bank
        )

        if remaining_dice == 6 and current_turn_score <= min_score * 6:
            return True

        if current_turn_score >= min_score * 2:
            return False

        if remaining_dice <= 2 and current_turn_score >= min_score:
            return False

        if game_phase == GamePhase.LATE and current_turn_score >= min_score * 3:
            return False

        if is_behind and current_turn_score < min_score * 4:
            return True

        return True

    def aggressive_strategy(self, current_turn_score: int, remaining_dice: int) -> bool:
        """
        Aggressive strategy - takes more risks to accumulate higher scores.

        Args:
            current_turn_score: Current score accumulated in this turn
            remaining_dice: Number of dice remaining to roll

        Returns:
            True to continue rolling, False to bank points
        """

        game_phase: GamePhase = self.get_game_phase()
        is_behind: bool = self.is_behind_leader()
        is_far_behind: bool = self.is_far_behind_leader()
        min_score: int = (
            30 if self.bot._game_ is None else self.bot._game_.config.min_score_to_bank
        )

        if remaining_dice == 6:
            return True

        if current_turn_score >= min_score * 5:
            return False

        if game_phase == GamePhase.LATE and current_turn_score >= min_score * 4:
            return False

        if is_behind and current_turn_score < min_score * 6:
            return True

        if is_far_behind and current_turn_score < min_score * 8:
            return True

        if remaining_dice <= 2 and current_turn_score < min_score * 4:
            return True

        return True

    def super_aggressive_strategy(
        self, current_turn_score: int, remaining_dice: int
    ) -> bool:
        """
        Super aggressive strategy - takes extreme risks, especially when behind.

        Args:
            current_turn_score: Current score accumulated in this turn
            remaining_dice: Number of dice remaining to roll

        Returns:
            True to continue rolling, False to bank points
        """

        game_phase: GamePhase = self.get_game_phase()
        is_far_behind: bool = self.is_far_behind_leader()
        min_score: int = (
            30 if self.bot._game_ is None else self.bot._game_.config.min_score_to_bank
        )

        if remaining_dice == 6:
            return True

        if current_turn_score >= min_score * 8:
            return False

        if is_far_behind and current_turn_score < min_score * 10:
            return True

        if remaining_dice == 1:
            return True

        if game_phase == GamePhase.EARLY and current_turn_score >= min_score * 6:
            return False

        return True

    def adaptive_strategy(self, current_turn_score: int, remaining_dice: int) -> bool:
        """
        Adaptive strategy - changes approach based on game phase.

        Args:
            current_turn_score: Current score accumulated in this turn
            remaining_dice: Number of dice remaining to roll

        Returns:
            True to continue rolling, False to bank points
        """

        game_phase: GamePhase = self.get_game_phase()

        if game_phase == GamePhase.EARLY:
            return self.conservative_strategy(current_turn_score, remaining_dice)
        elif game_phase == GamePhase.MIDDLE:
            return self.aggressive_strategy(current_turn_score, remaining_dice)
        else:  # GamePhase.LATE
            return self.super_aggressive_strategy(current_turn_score, remaining_dice)

    def copycat_strategy(self, current_turn_score: int, remaining_dice: int) -> bool:
        """
        Copycat strategy - imitates the most successful player's decisions.

        Args:
            current_turn_score: Current score accumulated in this turn
            remaining_dice: Number of dice remaining to roll

        Returns:
            True to continue rolling, False to bank points
        """

        if not self.bot._game_:
            return self.conservative_strategy(current_turn_score, remaining_dice)

        # Finding the most successful players
        successful_players = [
            p
            for p in self.bot._game_.players
            if p != self.bot and p.total_score > self.bot.total_score
        ]

        if not successful_players:
            return self.conservative_strategy(current_turn_score, remaining_dice)

        # Choose the most successful player
        best_player: Player = max(successful_players, key=lambda p: p.total_score)

        # Copying the strategy of the most successful player
        if isinstance(best_player, Bot):
            return best_player.make_decision(current_turn_score, remaining_dice)
        else:
            return self.aggressive_strategy(current_turn_score, remaining_dice)
