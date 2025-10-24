"""
Game module for the Zonk dice game.

This module implements the main game logic, including turn management,
round progression, win condition checking, and game flow control.
"""

from typing import Optional, TYPE_CHECKING
from project.assignment_4.zonk_dices import Dice, ScoreCalculator
from project.assignment_4.zonk_config import GameConfig

if TYPE_CHECKING:
    from zonk_players import Player


class Turn:
    """Represents a single player's turn in the game."""

    def __init__(self, player: "Player", dice: Dice) -> None:
        """
        Initialize a turn for a player.

        Args:
            player: The player taking the turn
            dice: Dice object for rolling
        """

        self.player: "Player" = player
        self.dice: Dice = dice
        self.current_score: int = 0
        self.is_zonk: bool = False
        self.used_dice: list[int] = []

    def play(self) -> int:
        """
        Execute one player's turn.

        The turn consists of rolling dice, calculating scores, and making
        decisions about whether to continue rolling or bank points.

        Returns:
            The score earned during this turn (0 if zonk or 555 rule triggered)
        """

        print(f"\n\n{self.player.name} turn:")

        remaining_dice = 6  # starting with 6 dices

        while True:
            # Rolling dices
            roll_result = self.dice.roll(remaining_dice)
            print(f"The roll: {roll_result}")

            # Scoring points
            score, used_dice = ScoreCalculator.calculate_score(roll_result)

            # Checking for zonk
            if score == 0:
                print("ZONK! There is no a single scoring-dice")
                self.is_zonk = True
                self.player.add_zonk()
                return 0

            # Updating the score for the turn
            self.current_score += score
            print(f"Scores for the roll: {score}")
            print(f"Scores for the turn: {self.current_score}")
            print()

            # Checking for the rule of 555
            if self.check_555_rule():
                return 0

            # Checking for the hot hand
            if len(used_dice) == remaining_dice:
                print(
                    "HOT HAND! All dices are scoring-dices; you can roll 6 dices again"
                )

                # Making decision
                if not self.player.make_decision(self.current_score, remaining_dice):
                    print(
                        f"{self.player.name} decides to stop and bank {self.current_score} points"
                    )
                    return self.current_score
                else:
                    print(
                        f"{self.player.name} decides to take some risk and rolls all 6 dices again"
                    )
                    remaining_dice = 6
                    continue

            # Updating the remaining dices
            remaining_dice = remaining_dice - len(used_dice)

            # Making decision
            if not self.player.make_decision(self.current_score, remaining_dice):
                print(
                    f"{self.player.name} decides to stop and bank {self.current_score} points"
                )
                return self.current_score

    def check_555_rule(self) -> bool:
        """
        Check if the 555 rule applies (player loses all points if total score becomes 555 points).

        Returns:
            True if the rule was triggered, False otherwise
        """

        total_after_turn = self.player.total_score + self.current_score
        if total_after_turn == 555:
            print(f"THE RULE OF 555! {self.player.name} loses ALL points!")
            self.player.total_score = 0
            return True
        return False


class Game:
    """Main game class that manages the overall game flow and state."""

    def __init__(self, config: Optional[GameConfig] = None) -> None:
        """
        Initialize the game with configuration.

        Args:
            config: Game configuration object. If None, uses default config.
        """

        self.config: GameConfig = config or GameConfig()
        self.dice: Dice = Dice()
        self.players: list["Player"] = []
        self.current_round: int = 0
        self.game_over: bool = False
        self.final_round: bool = False

    def add_player(self, player: "Player") -> None:
        """
        Add a player to the game.

        Args:
            player: Player object to add to the game
        """

        self.players.append(player)
        player.set_game(self)

    def play_round(self) -> None:
        """Execute one complete round where each active player takes a turn."""

        self.current_round += 1
        print(f"\n\n{'━'*50}")
        print(f"ROUND {self.current_round}")
        print(f"{'━'*50}")

        for player in self.players:
            if not player.is_active:
                continue

            turn = Turn(player, self.dice)
            turn_score = turn.play()

            # Zonk checking
            if turn.is_zonk:
                if player.consecutive_zonks == 3:
                    print(
                        f"THREE CONSECUTIVE ZONKS! Penalty: {self.config.zonk_penalty} points"
                    )
                    player.apply_penalty(self.config.zonk_penalty)
                    player.reset_zonk_counter()

                    # Checking for the rule of 555 after the penalty
                    if player.total_score == 555:
                        print(
                            f"THE RULE OF 555 after the penalty! {player.name} loses ALL points!"
                        )
                        player.total_score = 0
            else:
                # Successful turn — adding points
                player.total_score += turn_score
                player.reset_zonk_counter()
                print(f"Total score: {player.total_score}")

            # Checking for the win conditions
            if self.check_win_conditions():
                break

        # Showing status output after the round
        self.print_game_state()

    def check_win_conditions(self) -> bool:
        """
        Check if win conditions have been met.

        Returns:
            True if the game should end, False otherwise
        """

        # Checking for the achievement of the target score
        for player in self.players:
            if player.total_score >= self.config.target_score:
                if not self.final_round:
                    print(
                        f"\n{player.name} achieves {self.config.target_score} points! THE FINAL ROUND!"
                    )
                    self.final_round = True
                    return False
                else:
                    self.game_over = True
                    return True

        # Checking for the maximum number of rounds
        if self.current_round >= self.config.max_rounds:
            self.game_over = True
            return True

        return False

    def print_game_state(self) -> None:
        """Print the current state of the game after a round."""

        print(f"\n\nCURRENT STATE FOR ROUND {self.current_round}:")
        for player in self.players:
            print(f"{player}")

    def get_winner(self) -> Optional["Player"]:
        """
        Determine the winner of the game.

        Returns:
            The winning player object, or None if there's no winner
        """

        if not self.game_over:
            return None

        active_players = [p for p in self.players if p.is_active]
        if not active_players:
            return None

        # If there is only one player, then checking whether he won or not.
        if len(active_players) == 1:
            player = active_players[0]
            return player if player.total_score >= self.config.target_score else None

        # Finding the player with the highest score
        winner = max(active_players, key=lambda p: p.total_score)

        # Checking for the draw
        winners = [p for p in active_players if p.total_score == winner.total_score]
        if len(winners) > 1:
            print(
                "THE DRAW! Several players have finished the game with the same score:"
            )
            for w in winners:
                print(f"{w.name}")

        return winners[0] if winners else None

    def play_game(self) -> Optional["Player"]:
        """
        Play the complete game from start to finish.

        Returns:
            The winning player object, or None if there's no winner
        """

        print("THE BEGINNING OF THE ZONK GAME!")
        print(
            f"The goals: {self.config.target_score} points or {self.config.max_rounds} rounds"
        )

        while not self.game_over:
            self.play_round()

        # Completing the game
        winner = self.get_winner()

        if winner:
            print(f"\n{'━'*50}")
            print(f"THE WINNER: {winner.name} with {winner.total_score} points!")
            print(f"{'━'*50}")
        elif len(self.players) == 1:
            print(f"\n{'━'*50}")
            print(
                f"GAME OVER! {self.players[0].name} failed to reach {self.config.target_score} points in {self.config.max_rounds} rounds!"
            )
            print(f"Final score: {self.players[0].total_score} points")
            print(f"{'━'*50}")
        else:
            print("\nThe game is over without a winner")

        return winner
